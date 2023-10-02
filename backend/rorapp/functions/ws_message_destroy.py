def ws_message_destroy(class_name, instance_id) -> dict:
    '''
    Helper function for making a WebSocket message to destroy an instance.
    The message should be used to communicate with the frontend when an instance is destroyed.
    '''
    
    return {
        "operation": "destroy",
        "instance": {
            "class": class_name,
            "id": instance_id
        }
    }
