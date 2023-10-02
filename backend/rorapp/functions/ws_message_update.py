def ws_message_update(class_name, instance) -> dict:
    '''
    Helper function for making a WebSocket message to update an instance.
    The message should be used to communicate with the frontend when an instance is updated.
    '''
    
    return {
        "operation": "update",
        "instance": {
            "class": class_name,
            "data": instance
        }
    }