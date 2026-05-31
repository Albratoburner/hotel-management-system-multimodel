def generate_approval_request(intent_data: dict) -> dict:
    """
    Takes the parsed intent and formats it as an approval request for the frontend.
    """
    action = intent_data.get("action")
    
    if action == "CREATE_BOOKING":
        msg = (f"Please confirm: Book a {intent_data.get('room_type')} room for "
               f"{intent_data.get('guest_name')} from {intent_data.get('check_in_date')} "
               f"to {intent_data.get('check_out_date')}.")
    elif action == "CANCEL_BOOKING":
        msg = f"Please confirm: Cancel booking {intent_data.get('booking_id')}."
    elif action == "ISSUE_BONUS":
        msg = (f"Please confirm: Issue bonus of {intent_data.get('amount')} to "
               f"{intent_data.get('employee_name')} for {intent_data.get('reason')}.")
    elif action == "UPDATE_SALARY":
        msg = (f"Please confirm: Update salary for {intent_data.get('employee_name')} "
               f"to {intent_data.get('amount')}.")
    else:
        msg = "Please confirm the requested action."

    return {
        "status": "AWAITING_APPROVAL",
        "message": msg,
        "pending_intent": intent_data
    }
