'''
Anggota Kelompok:
Christopher Nathaniel Tanamas // 222200153
Elaine Evelyn // 222102311
Grace Callista Lim // 222102176
Gery Yulianto // 222101862

'''
class LRUPageFaultSimulator:
    def __init__(self, capacity):
        """
        Initialize the LRU Page Fault Simulator.
        
        :param capacity: Number of page frames in memory
        """
        self.capacity = capacity
        self.page_frames = [None] * capacity
        self.page_order = []
        self.page_faults = 0
        self.page_hits = 0

    def simulate_page_fault(self, page):
        """
        Simulate page reference and handle page fault/hit.
        
        :param page: Page being referenced
        """
        # Check if page is already in memory (page hit)
        if page in self.page_frames:
            self.page_hits += 1
            print(f"Page hit for page {page}. Page frames unchanged.")
            
            # Update page order to move this page to the end (most recently used)
            self.page_order.remove(page)
            self.page_order.append(page)
            return

        # Page fault occurs
        self.page_faults += 1
        print(f"Page fault for page {page}.", end=" ")

        # If there's space in page frames, simply add the page
        if None in self.page_frames:
            empty_index = self.page_frames.index(None)
            self.page_frames[empty_index] = page
            self.page_order.append(page)
        else:
            # Apply LRU algorithm to replace the least recently used page
            self.apply_lru_algorithm(page)

        # Display updated page frames
        print(f"Page frames after fault: {self.page_frames}")

    def apply_lru_algorithm(self, page):
        """
        Apply Least Recently Used (LRU) page replacement algorithm.
        
        :param page: New page to be added
        """
        # Find and remove the least recently used page
        lru_page = self.page_order[0]
        self.page_order.pop(0)
        
        # Replace the LRU page in page_frames
        lru_index = self.page_frames.index(lru_page)
        self.page_frames[lru_index] = page
        
        # Add new page to page_order
        self.page_order.append(page)

def main():
    # Get user input for page frames and page sequence
    capacity = int(input("Enter the number of page frames: "))
    page_sequence = input("Enter page sequence (space-separated): ").split()

    # Create LRU Page Fault Simulator
    simulator = LRUPageFaultSimulator(capacity)

    # Simulate page references
    for page in page_sequence:
        simulator.simulate_page_fault(page)

    # Display simulation summary
    print(f"\nTotal page faults: {simulator.page_faults}")
    print(f"Total page hits: {simulator.page_hits}")

if __name__ == "__main__":
    main()