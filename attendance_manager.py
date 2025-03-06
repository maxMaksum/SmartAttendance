from datetime import datetime, timedelta

class AttendanceManager:
    def __init__(self):
        # In-memory session store keyed by student_id.
        # Each record is a dict with: student_id, name, checkin_time, checkout_time, and state.
        self.session_store = {}

    def check_in(self, student_id, name=None):
        now = datetime.now()
        record = self.session_store.get(student_id)
        if record is None:
            # No record yet – create a new check-in record.
            new_record = {
                "student_id": student_id,
                "name": name,  # Store the name from check in.
                "checkin_time": now,
                "checkout_time": None,
                "state": "checked_in"
            }
            self.session_store[student_id] = new_record
            return {
                "status": "checked_in",
                "message": f"Student {student_id} ({name}) checked in at {now.strftime('%H:%M:%S')}."
            }
        else:
            # Optionally update the name if not already stored.
            if record.get("name") is None and name is not None:
                record["name"] = name
            # Use the appropriate timestamp based on current state.
            last_time = record["checkin_time"] if record["state"] == "checked_in" else record.get("checkout_time") or record["checkin_time"]
            if now - last_time < timedelta(minutes=1):
                return {
                    "status": "ignored",
                    "message": f"Student {student_id} scanned recently. Please wait."
                }
            if record["state"] == "checked_in":
                # Toggle to checked out.
                record["checkout_time"] = now
                record["state"] = "checked_out"
                self.session_store[student_id] = record
                return {
                    "status": "checked_out",
                    "message": f"Student {student_id} ({record.get('name')}) checked out at {now.strftime('%H:%M:%S')}."
                }
            else:
                # If already checked out, start a new attendance event (check in).
                new_record = {
                    "student_id": student_id,
                    "name": name if name else record.get("name"),
                    "checkin_time": now,
                    "checkout_time": None,
                    "state": "checked_in"
                }
                self.session_store[student_id] = new_record
                return {
                    "status": "checked_in",
                    "message": f"Student {student_id} ({new_record['name']}) checked in at {now.strftime('%H:%M:%S')}."
                }

    def save_records(self, database):
        """
        Save all session records to the specified database.
        """
        for record in self.session_store.values():
            database.save(record)

    def get_session_records(self):
        # Return all session records as a list.
        return list(self.session_store.values())
