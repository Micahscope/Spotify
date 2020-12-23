"""
 An object that represents a member of the Spotify plan.
 Each has 3 attributes: name, money owed, and Venmo User ID.
 The fourth attribute is used to write to the local data file.
"""


class Member:

    # Standard constructor function.
    def __init__(self, name, money_owed, uid):
        self.name = name
        self.money_owed = money_owed
        self.id = uid

    # This function is used to compare Member objects.
    def equals(self, person):

        if self.name == person.name:
            if self.money_owed == person.money_owed:
                if self.id == person.id:
                    return True
        return False

    # Returns the Member object's information separated
    # by tabs. Used in printing to files.
    def toString(self):
        return self.name + "\t" + str(self.money_owed) + "\t" + str(self.id)
