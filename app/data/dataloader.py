from promise import Promise
from promise.dataloader import DataLoader

class UserLoader(DataLoader):
    def batch_load_fn(self, keys):
        # Here we return a promise that will result on the
        # corresponding user for each key in keys
        #return Promise.resolve([get_user(id=key) for key in keys])

user_loader = UserLoader()

user_loader.load(1).then(lambda user: user_loader.load(user.best_friend_id))

user_loader.load(2).then(lambda user: user_loader.load(user.best_friend_id))