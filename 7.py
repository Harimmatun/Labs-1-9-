from pyee import EventEmitter

class ChatRoom(EventEmitter):
    def __init__(self):
        super().__init__()
        self.message_count = 0

    def send_message(self, sender, message):
        self.message_count += 1
        self.emit('message', sender, message, self.message_count)

class User:
    def __init__(self, name, chat_room):
        self.name = name
        self.chat_room = chat_room
        self.subscribed = False

    def subscribe(self):
        if not self.subscribed:
            self.chat_room.on('message', self.receive_message)
            self.subscribed = True
            print(f"{self.name} subscribed to chat")

    def unsubscribe(self):
        if self.subscribed:
            self.chat_room.remove_listener('message', self.receive_message)
            self.subscribed = False
            print(f"{self.name} unsubscribed from chat")

    def send_message(self, message):
        self.chat_room.send_message(self.name, message)

    def receive_message(self, sender, message, message_id):
        if sender != self.name:
            print(f"{self.name} received: '{message}' from {sender} (ID: {message_id})")

if __name__ == "__main__":
    print("Test 2: ChatRoom with Subscribe/Unsubscribe")
    chat_room = ChatRoom()
    alice = User("Alice", chat_room)
    bob = User("Bob", chat_room)

    alice.subscribe()
    bob.subscribe()

    alice.send_message("Hello, Bob!")
    bob.send_message("Hi, Alice!")

    bob.unsubscribe()
    alice.send_message("Are you there, Bob?")