class BloodRequestQueue:
    def __init__(self):
        self.items = []

    # Add request to the queue
    def enqueue(self, request):
        self.items.append(request)

    # Remove first request
    def dequeue(self):
        if not self.is_empty():
            return self.items.pop(0)
        return None

    # See first request
    def peek(self):
        if not self.is_empty():
            return self.items[0]
        return None

    # Check if queue is empty
    def is_empty(self):
        return len(self.items) == 0

    # Number of requests
    def size(self):
        return len(self.items)