def ws_message_create(class_name, instance) -> dict:
    '''
    Helper function for making a WebSocket message to create an instance.
    The message should be used to communicate with the frontend when an instance is created.
    '''
    
    return {
        "operation": "create",
        "instance": {
            "class": class_name,
            "data": instance
        }
    }
