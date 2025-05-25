from pyee import EventEmitter

class ChatRoom(EventEmitter):
    def __init__(self):
        super().__init__()
        self.message_count = 0

    def send_message(self, sender, message):
        self.message_count += 1
        self.emit('message', sender, message, self.message_count)

    def send_announcement(self, message):
        self.message_count += 1
        self.emit('announcement', message, self.message_count)

class User:
    def __init__(self, name, chat_room):
        self.name = name
        self.chat_room = chat_room
        self.subscribed = False
        self.log = []

    def subscribe(self):
        if not self.subscribed:
            self.chat_room.on('message', self.receive_message)
            self.chat_room.on('announcement', self.receive_announcement)
            self.chat_room.on('message', self.log_message)
            self.chat_room.on('announcement', self.log_message)
            self.subscribed = True
            print(f"{self.name} subscribed to chat")

    def unsubscribe(self):
        if self.subscribed:
            self.chat_room.remove_listener('message', self.receive_message)
            self.chat_room.remove_listener('announcement', self.receive_announcement)
            self.chat_room.remove_listener('message', self.log_message)
            self.chat_room.remove_listener('announcement', self.log_message)
            self.subscribed = False
            print(f"{self.name} unsubscribed from chat")

    def send_message(self, message):
        self.chat_room.send_message(self.name, message)

    def receive_message(self, sender, message, message_id):
        if sender != self.name:
            print(f"{self.name} received: '{message}' from {sender} (ID: {message_id})")

    def receive_announcement(self, message, message_id):
        print(f"{self.name} got announcement: '{message}' (ID: {message_id})")

    def log_message(self, *args):
        if len(args) == 3:
            sender, message, message_id = args
            self.log.append(f"Message from {sender}: '{message}' (ID: {message_id})")
        else:
            message, message_id = args
            self.log.append(f"Announcement: '{message}' (ID: {message_id})")

    def show_log(self):
        print(f"{self.name}'s log: {self.log}")

if __name__ == "__main__":
    print("Test 3: ChatRoom with Multiple Listeners")
    chat_room = ChatRoom()
    alice = User("Alice", chat_room)
    bob = User("Bob", chat_room)

    alice.subscribe()
    bob.subscribe()

    alice.send_message("Hello, Bob!")
    chat_room.send_announcement("Welcome to the chat!")
    bob.send_message("Hi, Alice!")

    alice.show_log()
    bob.show_log()

    bob.unsubscribe()
    alice.send_message("Bob, you there?")
    alice.show_log()