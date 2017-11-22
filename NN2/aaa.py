import uncompyle2
# with open("C:\Users\Norman\Desktop\Evolutionary-Neural-Network\NN2\food.py", "wb") as fileobj:
#     uncompyle2.uncompyle_file("C:\Users\Norman\Desktop\Evolutionary-Neural-Network\NN2\food.pyc", fileobj)
with open("bot.py", "wb") as fileobj:
    uncompyle2.uncompyle_file("bot.pyc", fileobj)