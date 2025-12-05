"""
Movie Ticket Booking With Seat Reservation (Multidimensional List + OOP)
Features implemented:
- 5 rows x 10 seats seating chart stored as a 2D list
- Book seats (mark as 'X' when booked)
- Front row seats cost more
- Offer student discount
- Print ticket with seat number and details
- Save bookings in a CSV file (bookings.csv) and load existing bookings on start
This is a console-based interactive program.
"""

import csv
import os
from datetime import datetime


class Theater:
    """Represents the movie theater seating and booking system."""

    def __init__(self, rows=5, cols=10, base_price=100, front_row_extra=50, student_discount=0.20):
        # Initialize basic configuration values
        self.rows = rows
        self.cols = cols
        self.base_price = base_price
        self.front_row_extra = front_row_extra
        self.student_discount = student_discount

        # Create seating as a 2D list (rows x cols). Initially every seat is available (marked 'O').
        # We'll use 'O' for open and 'X' for booked.
        self.seats = [['O' for _ in range(cols)] for _ in range(rows)]

        # Booking file path
        self.booking_file = 'bookings.csv'

        # Load any existing bookings from file so seats remain reserved across runs
        self._load_bookings()

    def display_seating(self):
        """Print a human-friendly seating chart with row/seat numbers."""
        print('\nSeating chart (O = open, X = booked)')
        # Print header for seat numbers
        header = '    ' + ' '.join(f'{i+1:>2}' for i in range(self.cols))
        print(header)
        print('   ' + '---' * self.cols)
        for r in range(self.rows):
            # row numbers start from 1 for user-friendliness
            row_str = f'R{r+1:<2}|' + ' '.join(f' {self.seats[r][c]}' for c in range(self.cols))
            print(row_str)
        print()

    def _seat_index_valid(self, row, seat):
        """Check if user-supplied row/seat indices are within range."""
        return 1 <= row <= self.rows and 1 <= seat <= self.cols

    def is_seat_available(self, row, seat):
        """Return True if the seat (1-based indices) is available."""
        if not self._seat_index_valid(row, seat):
            return False
        return self.seats[row-1][seat-1] == 'O'

    def calculate_price(self, row, is_student=False):
        """Calculate the ticket price depending on row and student discount."""
        price = self.base_price
        # More expensive for front row (row 1)
        if row == 1:
            price += self.front_row_extra
        # Apply student discount if applicable
        if is_student:
            price = price * (1 - self.student_discount)
        # Return integer rupee-style amount
        return round(price)

    def book_seat(self, name, row, seat, is_student=False):
        """Attempt to book a seat. If successful, mark it and save to file and return booking dict."""
        if not self._seat_index_valid(row, seat):
            raise ValueError('Row or seat number out of range.')
        if not self.is_seat_available(row, seat):
            raise ValueError('Requested seat is already booked.')

        # Mark the seat as booked
        self.seats[row-1][seat-1] = 'X'

        # Compute price and booking time
        price = self.calculate_price(row, is_student)
        timestamp = datetime.now().isoformat(sep=' ', timespec='seconds')

        # Booking record to save
        booking = {
            'name': name,
            'row': row,
            'seat': seat,
            'is_student': 'yes' if is_student else 'no',
            'price': price,
            'timestamp': timestamp
        }

        # Append to bookings file
        self._save_booking_to_file(booking)

        # Return booking details for printing ticket
        return booking

    def _save_booking_to_file(self, booking):
        """Append a booking record to CSV file. Create file with header if needed."""
        file_exists = os.path.exists(self.booking_file)
        with open(self.booking_file, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['name', 'row', 'seat', 'is_student', 'price', 'timestamp'])
            if not file_exists:
                writer.writeheader()
            writer.writerow(booking)

    def _load_bookings(self):
        """Load existing bookings from booking_file and mark seats as booked in the seating chart."""
        if not os.path.exists(self.booking_file):
            return
        try:
            with open(self.booking_file, mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        r = int(row['row'])
                        s = int(row['seat'])
                        # Defensive check before marking
                        if self._seat_index_valid(r, s):
                            self.seats[r-1][s-1] = 'X'
                    except Exception:
                        # Skip malformed rows silently
                        continue
        except Exception as e:
            print(f'Warning: could not read bookings file: {e}')


def print_ticket(booking):
    """Nicely prints the ticket details to the console."""
    ticket = []
    ticket.append('\n' + '='*40)
    ticket.append('            MOVIE TICKET')
    ticket.append('='*40)
    ticket.append(f"Name       : {booking['name']}")
    ticket.append(f"Seat       : Row {booking['row']} - Seat {booking['seat']}")
    ticket.append(f"Student    : {booking['is_student']}")
    ticket.append(f"Price      : {booking['price']}")
    ticket.append(f"Time       : {booking['timestamp']}")
    ticket.append('='*40 + '\n')
    print('\n'.join(ticket))


def main():
    # Create Theater instance with defaults
    theater = Theater()

    print('Welcome to the Movie Ticket Booking System')

    while True:
        print('\nChoose an option:')
        print('1) Show seating chart')
        print('2) Book a seat')
        print('3) Exit')
        choice = input('Enter choice (1-3): ').strip()

        if choice == '1':
            theater.display_seating()

        elif choice == '2':
            theater.display_seating()
            try:
                name = input('Enter your name: ').strip()
                # Row and seat numbers are 1-based for user
                row = int(input(f'Enter row (1-{theater.rows}): ').strip())
                seat = int(input(f'Enter seat (1-{theater.cols}): ').strip())
                student_input = input('Are you a student? (y/n): ').strip().lower()
                is_student = student_input.startswith('y')

                if not theater._seat_index_valid(row, seat):
                    print('Invalid row or seat number. Please try again.')
                    continue
                if not theater.is_seat_available(row, seat):
                    print('Sorry — that seat is already booked. Choose another.')
                    continue

                price = theater.calculate_price(row, is_student)
                confirm = input(f'Confirm booking Row {row} Seat {seat} — Price {price}. Confirm? (y/n): ').strip().lower()
                if not confirm.startswith('y'):
                    print('Booking cancelled.')
                    continue

                booking = theater.book_seat(name, row, seat, is_student)
                print('\nBooking successful!')
                print_ticket(booking)

            except ValueError as ve:
                print(f'Error: {ve}')
            except Exception as e:
                print(f'Unexpected error: {e}')

        elif choice == '3':
            print('Goodbye — thank you!')
            break

        else:
            print('Invalid option — enter 1, 2 or 3.')


if __name__ == '__main__':
    main()
