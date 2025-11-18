#!/usr/bin/env python3
"""
Test script for raw_memory OCR and URL extraction functionality.

This script tests:
1. OCR text extraction from screenshots
2. URL extraction (including domain-only formats like google.com)
3. Writing screenshot data to raw_memory table
4. Retrieving and verifying stored data

Usage:
    python tests/test_raw_memory_ocr.py
"""

import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from mirix.helpers.ocr_url_extractor import OCRUrlExtractor
from mirix.services.raw_memory_manager import RawMemoryManager
from mirix.schemas.user import User as PydanticUser


def test_ocr_extraction():
    """Test OCR text and URL extraction from images."""
    print("\n" + "=" * 80)
    print("TEST 1: OCR Text and URL Extraction")
    print("=" * 80)

    # Get test images directory
    images_dir = Path.home() / ".mirix" / "tmp" / "images"

    if not images_dir.exists():
        print(f"❌ Images directory not found: {images_dir}")
        return False

    # Get first few images for testing
    image_files = sorted(images_dir.glob("*.jpg"))[:5] + sorted(images_dir.glob("*.png"))[:2]

    if not image_files:
        print(f"❌ No image files found in {images_dir}")
        return False

    print(f"\n📁 Testing with {len(image_files)} images from: {images_dir}\n")

    ocr_extractor = OCRUrlExtractor()
    success_count = 0

    for image_path in image_files:
        print(f"\n📷 Processing: {image_path.name}")
        print("-" * 80)

        try:
            # Extract text and URLs
            ocr_text, urls = ocr_extractor.extract_urls_and_text(str(image_path))

            # Display results
            print(f"✅ OCR Text (first 200 chars):")
            print(f"   {ocr_text[:200] if ocr_text else '(No text extracted)'}...")

            if urls:
                print(f"\n✅ Extracted {len(urls)} URLs:")
                for url in urls:
                    print(f"   - {url}")
            else:
                print(f"\n⚠️  No URLs found")

            success_count += 1

        except Exception as e:
            print(f"❌ Error processing {image_path.name}: {e}")

    print(f"\n{'=' * 80}")
    print(f"✅ Successfully processed {success_count}/{len(image_files)} images")
    print(f"{'=' * 80}")

    return success_count == len(image_files)


def test_url_formats():
    """Test URL extraction for different formats."""
    print("\n" + "=" * 80)
    print("TEST 2: URL Format Recognition")
    print("=" * 80)

    # Test cases with different URL formats
    test_cases = [
        ("Visit https://github.com/user/repo for details", ["https://github.com/user/repo"]),
        ("Go to google.com for search", ["https://google.com"]),
        ("Check docs.python.org and stackoverflow.com", ["https://docs.python.org", "https://stackoverflow.com"]),
        ("URL: http://example.com/path/to/page", ["http://example.com/path/to/page"]),
        ("No URLs here e.g. just text i.e. nothing", []),
        ("Mixed: https://test.com and github.com/repo", ["https://test.com", "https://github.com/repo"]),
    ]

    extractor = OCRUrlExtractor()
    all_passed = True

    for i, (text, expected_urls) in enumerate(test_cases, 1):
        print(f"\nTest Case {i}:")
        print(f"  Input: {text}")
        print(f"  Expected: {expected_urls}")

        # Create a temporary test (this is a simplified test - in reality would need OCR)
        # For now, we test the regex patterns directly
        full_urls = extractor.FULL_URL_PATTERN.findall(text)
        domains = extractor.DOMAIN_PATTERN.findall(text)

        # Normalize URLs (same logic as in extract_urls_from_image)
        normalized_urls = []
        normalized_urls.extend(full_urls)

        for domain in domains:
            if any(domain in url for url in full_urls):
                continue
            if extractor._is_likely_url(domain):
                normalized_urls.append(f"https://{domain}")

        unique_urls = list(dict.fromkeys(normalized_urls))

        print(f"  Got:      {unique_urls}")

        # Check if results match expected
        if set(unique_urls) == set(expected_urls):
            print(f"  ✅ PASSED")
        else:
            print(f"  ❌ FAILED - Mismatch in URL extraction")
            all_passed = False

    print(f"\n{'=' * 80}")
    if all_passed:
        print("✅ All URL format tests PASSED")
    else:
        print("❌ Some URL format tests FAILED")
    print(f"{'=' * 80}")

    return all_passed


def test_raw_memory_storage():
    """Test writing and reading from raw_memory table."""
    print("\n" + "=" * 80)
    print("TEST 3: Raw Memory Database Storage")
    print("=" * 80)

    try:
        # Import database dependencies
        from mirix.server.server import db_context
        from mirix.orm import Organization
        from mirix.orm.user import User

        # Create manager
        raw_memory_manager = RawMemoryManager()

        print("\n✅ RawMemoryManager initialized")

        # Get or create test user
        with db_context() as session:
            # Try to get first user
            user = session.query(User).first()

            if not user:
                # Create test organization
                org = Organization(
                    id="test-org-123",
                    name="Test Organization"
                )
                session.add(org)

                # Create test user
                user = User(
                    id="test-user-123",
                    name="Test User",
                    timezone="UTC",
                    organization_id=org.id
                )
                session.add(user)
                session.commit()
                print(f"✅ Created test user: {user.id}")
            else:
                print(f"✅ Using existing user: {user.id}")

            # Convert to Pydantic model
            pydantic_user = PydanticUser(
                id=user.id,
                name=user.name,
                timezone=user.timezone,
                organization_id=user.organization_id
            )

        # Test data
        test_screenshots = [
            {
                "screenshot_path": "/Users/power/.mirix/tmp/images/test1.jpg",
                "source_app": "Chrome",
                "ocr_text": "Welcome to GitHub! Visit github.com for more info.",
                "urls": ["https://github.com"]
            },
            {
                "screenshot_path": "/Users/power/.mirix/tmp/images/test2.png",
                "source_app": "Safari",
                "ocr_text": "Search on google.com or check docs.python.org",
                "urls": ["https://google.com", "https://docs.python.org"]
            },
            {
                "screenshot_path": "/Users/power/.mirix/tmp/images/test3.jpg",
                "source_app": "Firefox",
                "ocr_text": "No URLs in this screenshot, just plain text",
                "urls": []
            }
        ]

        print(f"\n📝 Inserting {len(test_screenshots)} test records...")
        inserted_ids = []

        for i, test_data in enumerate(test_screenshots, 1):
            print(f"\n  Record {i}:")
            print(f"    App: {test_data['source_app']}")
            print(f"    Text: {test_data['ocr_text'][:50]}...")
            print(f"    URLs: {test_data['urls']}")

            raw_memory = raw_memory_manager.insert_raw_memory(
                actor=pydantic_user,
                screenshot_path=test_data["screenshot_path"],
                source_app=test_data["source_app"],
                captured_at=datetime.now(timezone.utc),
                ocr_text=test_data["ocr_text"],
                source_url=test_data["urls"][0] if test_data["urls"] else None,
                metadata={"test_urls": test_data["urls"], "test_index": i}
            )

            inserted_ids.append(raw_memory.id)
            print(f"    ✅ Inserted with ID: {raw_memory.id}")

        print(f"\n✅ Successfully inserted {len(inserted_ids)} records")

        # Test retrieval
        print(f"\n📖 Testing retrieval...")

        for raw_memory_id in inserted_ids:
            retrieved = raw_memory_manager.get_raw_memory_by_id(
                raw_memory_id=raw_memory_id,
                user_id=pydantic_user.id
            )

            if retrieved:
                print(f"  ✅ Retrieved {raw_memory_id}:")
                print(f"     App: {retrieved.source_app}")
                print(f"     URL: {retrieved.source_url}")
                print(f"     OCR: {retrieved.ocr_text[:50] if retrieved.ocr_text else 'None'}...")
            else:
                print(f"  ❌ Failed to retrieve {raw_memory_id}")
                return False

        # Test bulk retrieval
        print(f"\n📦 Testing bulk retrieval...")
        bulk_retrieved = raw_memory_manager.get_raw_memories_by_ids(
            raw_memory_ids=inserted_ids,
            user_id=pydantic_user.id
        )

        print(f"  ✅ Retrieved {len(bulk_retrieved)} records in bulk")

        # Test filtering by source_app
        print(f"\n🔍 Testing filter by source_app...")
        chrome_memories = raw_memory_manager.get_raw_memories_by_source_app(
            user_id=pydantic_user.id,
            organization_id=pydantic_user.organization_id,
            source_app="Chrome"
        )
        print(f"  ✅ Found {len(chrome_memories)} Chrome screenshots")

        # Clean up test data
        print(f"\n🧹 Cleaning up test data...")
        for raw_memory_id in inserted_ids:
            raw_memory_manager.delete_raw_memory(raw_memory_id)
        print(f"  ✅ Deleted {len(inserted_ids)} test records")

        print(f"\n{'=' * 80}")
        print("✅ All database storage tests PASSED")
        print(f"{'=' * 80}")

        return True

    except Exception as e:
        print(f"\n❌ Database storage test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("🧪 MIRIX Raw Memory OCR Test Suite")
    print("=" * 80)

    results = {
        "OCR Extraction": False,
        "URL Format Recognition": False,
        "Database Storage": False
    }

    # Run tests
    try:
        results["OCR Extraction"] = test_ocr_extraction()
    except Exception as e:
        print(f"\n❌ OCR Extraction test crashed: {e}")
        import traceback
        traceback.print_exc()

    try:
        results["URL Format Recognition"] = test_url_formats()
    except Exception as e:
        print(f"\n❌ URL Format test crashed: {e}")
        import traceback
        traceback.print_exc()

    try:
        results["Database Storage"] = test_raw_memory_storage()
    except Exception as e:
        print(f"\n❌ Database Storage test crashed: {e}")
        import traceback
        traceback.print_exc()

    # Print summary
    print("\n" + "=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)

    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"  {test_name}: {status}")

    all_passed = all(results.values())

    print("\n" + "=" * 80)
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
    else:
        print("⚠️  SOME TESTS FAILED")
    print("=" * 80 + "\n")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
