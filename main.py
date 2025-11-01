import csv
import os

class Room:
    """
    Represents a classroom room with unique ID, building, capacity, and booked hours.
    
    Design choice: Using a set for booked_hours for O(1) lookup and no duplicates.
    Hours are integers from 0 to 23.
    """
    def __init__(self, room_no, building, capacity):
        self.room_no = room_no
        self.building = building
        self.capacity = capacity
        self.booked_hours = set()

    def book_hour(self, hour):
        """Book a specific hour if available."""
        if hour in self.booked_hours:
            raise ValueError(f"Hour {hour} is already booked for room {self.room_no}.")
        if not 0 <= hour <= 23:
            raise ValueError("Hour must be between 0 and 23.")
        self.booked_hours.add(hour)

    def is_free_at_hour(self, hour):
        """Check if the room is free at a given hour."""
        return hour not in self.booked_hours

    def cancel_hour(self, hour):
        """Cancel a booking for a specific hour."""
        if hour not in self.booked_hours:
            raise ValueError(f"Hour {hour} is not booked for room {self.room_no}.")
        if not 0 <= hour <= 23:
            raise ValueError("Hour must be between 0 and 23.")
        self.booked_hours.remove(hour)

    def get_booked_hours_str(self):
        """Return booked hours as semicolon-separated string for CSV."""
        if not self.booked_hours:
            return ""
        return ";".join(map(str, sorted(self.booked_hours)))

    @classmethod
    def from_csv_row(cls, row):
        """Create Room instance from CSV row."""
        room_no, building, capacity_str, booked_hours_str = row
        capacity = int(capacity_str)
        room = cls(room_no, building, capacity)
        if booked_hours_str:
            for hour_str in booked_hours_str.split(";"):
                room.booked_hours.add(int(hour_str))
        return room

class RoomManager:
    """
    Manages a collection of rooms, handling additions, bookings, searches, and views.
    
    Design choice: Single responsibility for room operations. Uses list for rooms
    (simplicity, as uniqueness is enforced on add). Room_no is globally unique.
    """
    def __init__(self):
        self.rooms = []

    def add_room(self, room_no, building, capacity):
        """Add a new room if room_no is unique."""
        if capacity <= 0:
            raise ValueError("Capacity must be positive.")
        for room in self.rooms:
            if room.room_no == room_no:
                raise ValueError(f"Room with ID '{room_no}' already exists.")
        self.rooms.append(Room(room_no, building, capacity))

    def book_room(self, room_no, hour):
        """Book a room for a specific hour."""
        room = self._find_room(room_no)
        if room is None:
            raise ValueError(f"Room '{room_no}' not found.")
        room.book_hour(hour)

    def cancel_booking(self, room_no, hour):
        """Cancel a booking for a specific hour."""
        room = self._find_room(room_no)
        if room is None:
            raise ValueError(f"Room '{room_no}' not found.")
        room.cancel_hour(hour)

    def find_rooms(self, building=None, min_capacity=None, hour=None):
        """
        Find rooms matching criteria:
        - building: exact match (case-sensitive)
        - min_capacity: >= value
        - hour: free at that hour (if provided)
        """
        matching = []
        for room in self.rooms:
            if building and room.building != building:
                continue
            if min_capacity and room.capacity < min_capacity:
                continue
            if hour is not None:
                if not room.is_free_at_hour(hour):
                    continue
            matching.append(room)
        return matching

    def view_room(self, room_no):
        """View details and bookings for a room."""
        room = self._find_room(room_no)
        if room is None:
            raise ValueError(f"Room '{room_no}' not found.")
        return room

    def _find_room(self, room_no):
        """Helper to find a room by ID."""
        for room in self.rooms:
            if room.room_no == room_no:
                return room
        return None

    def load_from_csv(self, filename="bookings_final_state.csv"):
        """Load rooms from CSV if file exists."""
        if not os.path.exists(filename):
            print("No existing CSV file found. Starting with empty rooms.")
            return
        try:
            with open(filename, 'r', newline='') as file:
                reader = csv.reader(file)
                next(reader)  # Skip header
                for row in reader:
                    if row:  # Skip empty rows
                        self.rooms.append(Room.from_csv_row(row))
            print(f"Loaded {len(self.rooms)} rooms from {filename}.")
        except Exception as e:
            print(f"Error loading CSV: {e}. Starting with empty rooms.")

    def save_to_csv(self, filename="bookings_final_state.csv"):
        """Save all rooms to CSV."""
        try:
            with open(filename, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['room_no', 'building', 'capacity', 'booked_hours'])
                for room in self.rooms:
                    writer.writerow([
                        room.room_no,
                        room.building,
                        room.capacity,
                        room.get_booked_hours_str()
                    ])
            print(f"Saved {len(self.rooms)} rooms to {filename}.")
        except Exception as e:
            print(f"Error saving CSV: {e}.")

def display_menu():
    """Display the main menu."""
    print("\n=== Class Room Booking System ===")
    print("1. Add a new room")
    print("2. Book a room")
    print("3. Find available rooms")
    print("4. View room details and bookings")
    print("5. Cancel a room booking")
    print("6. Exit")

def get_user_input(prompt, type_func=str, default=None):
    """Get user input with optional default."""
    if default is not None:
        inp = input(f"{prompt} (or press Enter for default '{default}'): ").strip()
    else:
        inp = input(f"{prompt}: ").strip()
    if not inp:
        return default
    try:
        return type_func(inp)
    except ValueError:
        if default is not None:
            print("Invalid input. Using default.")
            return default
        else:
            print("Invalid input.")
            return None

def main():
    """Main menu-driven loop."""
    manager = RoomManager()
    manager.load_from_csv()

    while True:
        display_menu()
        choice = input("Enter your choice (1-6): ").strip()

        try:
            if choice == "1":
                room_no = get_user_input("Enter room ID:", str, None)
                if not room_no:
                    print("Room ID is required.")
                    continue
                building = get_user_input("Enter building name:", str, None)
                if not building:
                    print("Building name is required.")
                    continue
                capacity_str = get_user_input("Enter capacity:", str, None)
                if not capacity_str:
                    print("Capacity is required.")
                    continue
                try:
                    capacity = int(capacity_str)
                except ValueError:
                    print("Invalid capacity. Must be a number.")
                    continue
                manager.add_room(room_no, building, capacity)
                print(f"Room '{room_no}' added successfully.")

            elif choice == "2":
                room_no = get_user_input("Enter room ID to book:", str, None)
                if not room_no:
                    print("Room ID is required.")
                    continue
                hour_str = get_user_input("Enter hour (0-23):", str, None)
                if not hour_str:
                    print("Hour is required.")
                    continue
                try:
                    hour = int(hour_str)
                except ValueError:
                    print("Invalid hour. Must be a number.")
                    continue
                manager.book_room(room_no, hour)
                print(f"Room '{room_no}' booked for hour {hour}.")

            elif choice == "3":
                building = get_user_input("Enter building (optional):", str, None)
                min_cap_str = get_user_input("Enter minimum capacity (optional):", str, None)
                min_capacity = int(min_cap_str) if min_cap_str else None
                hour_str = get_user_input("Enter hour to check availability (optional):", str, None)
                hour = int(hour_str) if hour_str else None

                rooms = manager.find_rooms(building, min_capacity, hour)
                if not rooms:
                    print("No rooms match the criteria.")
                else:
                    print(f"\nFound {len(rooms)} room(s):")
                    for room in rooms:
                        status = "free" if hour is None or room.is_free_at_hour(hour) else "booked"
                        print(f"- {room.room_no} ({room.building}, cap: {room.capacity}) - {status} at hour {hour}" if hour else f"- {room.room_no} ({room.building}, cap: {room.capacity})")

            elif choice == "4":
                room_no = get_user_input("Enter room ID to view:", str, None)
                if not room_no:
                    print("Room ID is required.")
                    continue
                room = manager.view_room(room_no)
                print(f"\nRoom: {room.room_no}")
                print(f"Building: {room.building}")
                print(f"Capacity: {room.capacity}")
                print(f"Booked hours: {sorted(room.booked_hours) if room.booked_hours else 'None'}")

            elif choice == "5":
                room_no = get_user_input("Enter room ID to cancel booking:", str, None)
                if not room_no:
                    print("Room ID is required.")
                    continue
                hour_str = get_user_input("Enter hour to cancel (0-23):", str, None)
                if not hour_str:
                    print("Hour is required.")
                    continue
                try:
                    hour = int(hour_str)
                except ValueError:
                    print("Invalid hour. Must be a number.")
                    continue
                manager.cancel_booking(room_no, hour)
                print(f"Booking cancelled for room '{room_no}' at hour {hour}.")

            elif choice == "6":
                manager.save_to_csv()
                print("Exiting.")
                break

            else:
                print("Invalid choice. Please try again.")

        except ValueError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()
