/**
 * Request Queue Manager
 * 
 * This utility manages HTTP requests to prevent blocking when streaming requests are active.
 * It separates streaming requests from regular requests and ensures regular requests
 * don't get blocked by long-running streaming operations.
 */

class RequestQueueManager {
  constructor() {
    // Track active streaming requests
    this.activeStreamingRequests = new Set();

    // Queue for regular (non-streaming) requests
    this.regularRequestQueue = [];

    // Priority queue for high-priority requests (e.g., health checks)
    this.priorityRequestQueue = [];

    // Track if we're currently processing the queue
    this.isProcessingQueue = false;

    // Maximum concurrent regular requests when streaming is active
    // Increased from 2 to 10 to prevent queue timeout when loading multiple memory types
    this.maxConcurrentRegularRequests = 10;
    this.currentRegularRequests = 0;
  }

  /**
   * Make a streaming request (doesn't go through the queue)
   */
  async makeStreamingRequest(url, options = {}) {
    const requestId = `stream_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

    try {
      this.activeStreamingRequests.add(requestId);

      // Make the streaming request directly
      const response = await fetch(url, options);

      return {
        response,
        cleanup: () => {
          this.activeStreamingRequests.delete(requestId);
          // Process any queued requests when streaming ends
          this.processQueue();
        }
      };
    } catch (error) {
      this.activeStreamingRequests.delete(requestId);
      this.processQueue();
      throw error;
    }
  }

  /**
   * Make a regular request (goes through queue if streaming is active)
   */
  async makeRegularRequest(url, options = {}) {
    const isPriority = options.isPriority === true;

    console.log(`[Queue] Requesting: ${url} (Priority: ${isPriority}) | Active: ${this.currentRegularRequests}/${this.maxConcurrentRegularRequests} | Queued: ${this.priorityRequestQueue.length}P/${this.regularRequestQueue.length}R`);

    return new Promise((resolve, reject) => {
      const requestData = {
        url,
        options,
        resolve,
        reject,
        timestamp: Date.now()
      };

      // Priority requests always execute immediately, ignoring the limit
      if (isPriority) {
        console.log(`[Queue] Executing priority request immediately (bypassing limit): ${url}`);
        this.executeRequest(requestData);
        // Don't return here - let executeRequest handle resolve/reject
      }
      // If no streaming requests are active and we haven't hit the limit, execute immediately
      else if (this.activeStreamingRequests.size === 0 &&
        this.currentRegularRequests < this.maxConcurrentRegularRequests) {
        console.log(`[Queue] Executing regular request immediately: ${url}`);
        this.executeRequest(requestData);
      } else {
        // Queue the request (regular only, since priority is always executed)
        console.log(`[Queue] Queueing regular request: ${url}`);
        this.regularRequestQueue.push(requestData);
        this.processQueue();
      }
    });
  }

  /**
   * Execute a request immediately
   */
  async executeRequest(requestData) {
    this.currentRegularRequests++;

    try {
      const response = await fetch(requestData.url, requestData.options);
      requestData.resolve(response);
    } catch (error) {
      requestData.reject(error);
    } finally {
      this.currentRegularRequests--;
      // Process more queued requests
      setTimeout(() => this.processQueue(), 0);
    }
  }

  /**
   * Process the queue of regular requests
   * Priority requests are processed first
   */
  async processQueue() {
    if (this.isProcessingQueue ||
      (this.priorityRequestQueue.length === 0 && this.regularRequestQueue.length === 0)) {
      return;
    }

    this.isProcessingQueue = true;

    try {
      while ((this.priorityRequestQueue.length > 0 || this.regularRequestQueue.length > 0) &&
        this.currentRegularRequests < this.maxConcurrentRegularRequests) {

        // Process priority queue first
        const requestData = this.priorityRequestQueue.length > 0
          ? this.priorityRequestQueue.shift()
          : this.regularRequestQueue.shift();

        // Check if request is too old (60 seconds) and reject it
        // Increased from 30s to 60s to accommodate slower API responses
        if (Date.now() - requestData.timestamp > 60000) {
          requestData.reject(new Error('Request timeout - queued too long'));
          continue;
        }

        // Execute the request
        this.executeRequest(requestData);
      }
    } finally {
      this.isProcessingQueue = false;
    }
  }

  /**
   * Get queue status for debugging
   */
  getStatus() {
    return {
      activeStreamingRequests: this.activeStreamingRequests.size,
      queuedPriorityRequests: this.priorityRequestQueue.length,
      queuedRegularRequests: this.regularRequestQueue.length,
      currentRegularRequests: this.currentRegularRequests
    };
  }

  /**
   * Clear the queue (useful for cleanup)
   */
  clearQueue() {
    // Reject all priority requests
    while (this.priorityRequestQueue.length > 0) {
      const requestData = this.priorityRequestQueue.shift();
      requestData.reject(new Error('Request queue cleared'));
    }

    // Reject all regular requests
    while (this.regularRequestQueue.length > 0) {
      const requestData = this.regularRequestQueue.shift();
      requestData.reject(new Error('Request queue cleared'));
    }
  }
}

// Create a singleton instance
const requestQueue = new RequestQueueManager();

/**
 * Enhanced fetch function that uses the request queue
 */
export const queuedFetch = (url, options = {}) => {
  // Determine if this is a streaming request
  const isStreaming = url.includes('/send_streaming_message') ||
    options.isStreaming === true;

  if (isStreaming) {
    return requestQueue.makeStreamingRequest(url, options);
  } else {
    return requestQueue.makeRegularRequest(url, options);
  }
};

// Export the queue manager for debugging
export const getRequestQueueStatus = () => requestQueue.getStatus();
export const clearRequestQueue = () => requestQueue.clearQueue();

export default queuedFetch; 