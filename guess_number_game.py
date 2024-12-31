
import random

def guess_number_game():
    number_to_guess = random.randint(1, 100)
    attempts = 0
    print("欢迎来到猜数字游戏！")
    print("我已经想好了一个1到100之间的数字。来试试能否猜到它吧！")

    while True:
        guess = input("请输入你的猜测：")
        try:
            guess = int(guess)
            attempts += 1
            if guess < number_to_guess:
                print("太小了！再试一次。")
            elif guess > number_to_guess:
                print("太大了！再试一次。")
            else:
                print(f"恭喜你！你猜对了！数字是 {number_to_guess}。")
                print(f"你总共尝试了 {attempts} 次。")
                break
        except ValueError:
            print("请输入一个有效的整数。")

# 运行游戏
guess_number_game()
