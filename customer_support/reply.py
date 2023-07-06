import time

class Reply:
    def __init__(self, replyID, userID, ticketID, Content):
        self.replyID = replyID
        self.userID = userID
        self.ticketID = ticketID
        self.content = Content
        self.created_at = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        self.updated_at = None
        self.deleted_at = None

    def editReply(self, newContent):
        if self.content == None:
            raise ValueError("This reply does not exist...")
        self.content = newContent
        self.updated_at = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    def deleteReply(self):
        if self.content == None:
            raise ValueError("This reply does not exist...")
        self.content = None
        self.deleted_at = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    def readReply(self):
        if self.content:
            return self.content
        else:
            return "This reply does not exist..."
        


if __name__ == "__main__":
    # test cases 
    reply1 = Reply(1, 1, 1, "I am having trouble with my account")
    print(reply1.readReply())
    reply1.editReply("I am having trouble with my account, please help me")
    print(reply1.readReply())
    reply1.deleteReply()
    print(reply1.readReply())
    reply1.editReply("I am having trouble with my account, please help me")
    print(reply1.readReply())