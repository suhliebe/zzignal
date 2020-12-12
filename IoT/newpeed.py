import random

def findMinIdex(ary):
    minIdx = 0
    for i in range(1, len(ary)):
        if(ary[minIdx]> ary[i]):
            minIdx = i

    return minIdx

## 함수 선언부
before = [random.randint(10,99) for _ in range(20)]
after = []


## 전역 변수부
print('정렬전 -->', before)
for _ in range(len(before)):
    minPos = findMinIdex(before)
    after.append(before[minPos])
    del(before[minPos])

print('정렬후 -->',after)