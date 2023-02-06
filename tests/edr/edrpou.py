def _validateEdrpou(code):
    class_1 = {}
    class_1['case_1'] = [1, 2, 3, 4, 5, 6, 7]
    class_1['case_2'] = [3, 4, 5, 6, 7, 8, 9]

    class_2 = {}
    class_2['case_1'] = [7, 1, 2, 3, 4, 5, 6]
    class_2['case_2'] = [9, 3, 4, 5, 6, 7, 8]

    cluster = {}
    cluster['class_1'] = class_1
    cluster['class_2'] = class_2

    codeInt = int(code, base=10)
    if (codeInt > 30000000 and codeInt < 60000000):
        classType = "class_2"
    else:
        classType = "class_1"

    arrIndexes = cluster[classType]
    arrCodeItems = list(code)

    arrIndex = arrIndexes['case_1']
    kSumm = 0

    for i in range(0, len(arrCodeItems) - 1):
        kSumm += int(arrCodeItems[i], base=10) * arrIndex[i]

    kDigit = kSumm % 11

    if kDigit > 9:
        kSumm = 0
        kDigit = 0
        arrIndex = arrIndexes['case_2']
        for i in range(0, len(arrCodeItems) - 1):
            kSumm += int(arrCodeItems[i], base=10) * arrIndex[i]
        kDigit = kSumm % 11
        if kDigit > 9:
            kDigit = 0
    else:
        pass

    codeKD = int(code[-1], base=10)
    return kDigit == codeKD


codes = [
    '03764809',
    '03793449',
    '24410808',
    '05465755',
    '00381516',
    '36280990'
]

for code in codes:
    res = _validateEdrpou(code)
    print('Code {} is {}'.format(code, res))
