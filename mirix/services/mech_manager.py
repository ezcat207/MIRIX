import threading
import time
import os
import json
import logging
from datetime import datetime
from typing import List, Dict, Optional, Any
from pydantic import BaseModel

# Configure logging
logger = logging.getLogger(__name__)

class MechState(BaseModel):
    mode: str = "HANGAR"  # HANGAR, COCKPIT, DEBRIEF
    active_mech_id: Optional[str] = None
    start_time: Optional[datetime] = None
    session_data: Dict[str, Any] = {}

class Mech(BaseModel):
    id: str
    name: str
    type: str = "Generic"
    status: str = "Standby"
    path: Optional[str] = None
    why: Optional[str] = None
    what: Optional[str] = None
    tasks: List[Dict[str, Any]] = []  # Changed from List[str] to List[Dict]

class MechManager:
    def __init__(self, projects_path: str):
        self.projects_path = projects_path
        self.state = MechState()
        self.mechs: List[Mech] = []
        self.last_mtime = 0
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self.lock = threading.Lock()
        
        # Mock daily history (OKR-related and unrelated)
        self.daily_history = [
            {
                "title": "设计 Phase 2 数据本体 (Ontology)",
                "time": "2025-11-24T08:30:00",
                "mech_id": "mech-0",
                "okr_related": True
            },
            {
                "title": "回复客户邮件",
                "time": "2025-11-24T09:15:00",
                "mech_id": None,  # Not from a mech
                "okr_related": False
            },
            {
                "title": "读睡前故事《小王子》第三章",
                "time": "2025-11-24T10:00:00",
                "mech_id": "mech-1",
                "okr_related": True
            },
            {
                "title": "刷 Twitter",
                "time": "2025-11-24T11:30:00",
                "mech_id": None,
                "okr_related": False
            }
        ]

    def start(self):
        """Start the file watcher thread."""
        if self._thread is None:
            self._stop_event.clear()
            self._thread = threading.Thread(target=self._poll_loop, daemon=True)
            self._thread.start()
            self._load_daily_history_from_db() # Load history from DB
            logger.info(f"MechManager started watching: {self.projects_path}")

    def stop(self):
        """Stop the file watcher thread."""
        if self._thread:
            self._stop_event.set()
            self._thread.join()
            self._thread = None

    def _poll_loop(self):
        """Poll the projects file for changes."""
        while not self._stop_event.is_set():
            try:
                if os.path.exists(self.projects_path):
                    mtime = os.path.getmtime(self.projects_path)
                    if mtime > self.last_mtime:
                        self.last_mtime = mtime
                        self._reload_projects()
            except Exception as e:
                logger.error(f"Error polling projects file: {e}")
            
            time.sleep(5)  # Poll every 5 seconds

    def _reload_projects(self):
        """Parse the projects JSON file."""
        try:
            with open(self.projects_path, 'r', encoding='utf-8') as f:
                content = json.load(f)
            
            new_mechs = []
            for item in content:
                # Convert tasks dicts to list of dicts if needed
                tasks = item.get("tasks", [])
                
                mech = Mech(
                    id=item.get("id", f"mech-{len(new_mechs)}"),
                    name=item.get("name", "Unknown"),
                    type=item.get("type", "Project"),
                    status=item.get("status", "Ready"),
                    why=item.get("why"),
                    what=item.get("what"),
                    tasks=tasks
                )
                new_mechs.append(mech)
            
            with self.lock:
                self.mechs = new_mechs
                logger.info(f"Reloaded {len(self.mechs)} mechs from {self.projects_path}")
                
        except Exception as e:
            logger.error(f"Failed to reload projects: {e}")

    def _parse_markdown(self, content: str) -> List[Mech]:
        """Deprecated: Logic moved to _reload_projects for JSON"""
        return []

    # --- Public API ---

    def get_status(self) -> Dict[str, Any]:
        with self.lock:
            return {
                "state": self.state.dict(),
                "mechs": [m.dict() for m in self.mechs],
                "pilot_metrics": { # Mock data for now, will connect to DB later
                    "capability": 85,
                    "wealth": 42,
                    "influence": 60
                },
                "daily_history": getattr(self, "daily_history", []) # Return daily history
            }

    def launch_mech(self, mech_id: str) -> bool:
        with self.lock:
            # Validate mech_id
            mech = next((m for m in self.mechs if m.id == mech_id), None)
            if not mech:
                return False
            
            self.state.mode = "COCKPIT"
            self.state.active_mech_id = mech_id
            self.state.start_time = datetime.utcnow()
            self.state.session_data = {"tasks_completed": []}
            return True

    def complete_task(self, task_title: str):
        with self.lock:
            if self.state.mode == "COCKPIT":
                task_entry = {
                    "title": task_title,
                    "time": datetime.utcnow().isoformat(),
                    "mech_id": self.state.active_mech_id
                }
                self.state.session_data["tasks_completed"].append(task_entry)
                
                # Add to daily history
                if not hasattr(self, "daily_history"):
                    self.daily_history = []
                self.daily_history.append(task_entry)

    def debrief_session(self, reflection: str, metrics: Dict[str, float]):
        with self.lock:
            if self.state.mode != "COCKPIT" and self.state.mode != "DEBRIEF":
                return False
            
            end_time = datetime.utcnow()
            
            # Save to Database
            try:
                from mirix.database.sqlite_functions import session_scope
                from mirix.orm.mech_session import MechSession
                
                with session_scope() as session:
                    db_session = MechSession(
                        mech_id=self.state.active_mech_id,
                        start_time=self.state.start_time,
                        end_time=end_time,
                        reflection=reflection,
                        tasks_completed=self.state.session_data.get("tasks_completed", []),
                        # Metrics
                        wealth_generated=metrics.get("wealth", 0.0),
                        influence_gained=metrics.get("influence", 0.0),
                        capability_growth=metrics.get("capability", 0.0),
                        focus_score=metrics.get("focus", 0.0)
                    )
                    session.add(db_session)
                    logger.info(f"Saved MechSession to DB: {db_session}")
            except Exception as e:
                logger.error(f"Failed to save session to DB: {e}")

            # Reset state
            self.state.mode = "HANGAR"
            self.state.active_mech_id = None
            self.state.start_time = None
            self.state.session_data = {}
            return True

    def _load_daily_history_from_db(self):
        """Load today's completed tasks from DB."""
        try:
            from mirix.database.sqlite_functions import session_scope
            from mirix.orm.mech_session import MechSession
            from sqlalchemy import func
            
            today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            
            with session_scope() as session:
                todays_sessions = session.query(MechSession).filter(MechSession.end_time >= today_start).all()
                
                history = []
                for s in todays_sessions:
                    if s.tasks_completed:
                        for t in s.tasks_completed:
                            # Ensure task has okr_related flag (default True for mech tasks)
                            if "okr_related" not in t:
                                t["okr_related"] = True 
                            history.append(t)
                
                # Merge with mock data for now (optional, can remove mock later)
                # self.daily_history.extend(history)
                # For now, let's just use the DB history + existing mock
                existing_mock = getattr(self, "daily_history", [])
                self.daily_history = existing_mock + history
                
        except Exception as e:
            logger.error(f"Failed to load daily history: {e}")

# Singleton instance (initialized in main or server)
# mech_manager = MechManager("/path/to/projects.md")
