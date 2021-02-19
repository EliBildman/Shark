num_tests = 666666

for i in range(num_tests):
        if int(i / num_tests * 10) - int((i - 1) / num_tests * 10) > 0:
            print(int(i / num_tests * 100), '% completed')