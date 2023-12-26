def bullets_to_str(bullets):
    pass

def split_bullets(bullet_str):
    bullet_str = bullet_str.split("#")
    bullet_str = [bullet_str[i].split(":") for i in range(len(bullet_str))]
    for index, i in enumerate(bullet_str):
        bullet_str[index] = list(map(int, bullet_str[index]))
    return bullet_str
    

def test_update_data():
    data = "1;250:250;8;25:450#35:54#230:220"
    res = update_data(data)
    print(res)
    i = 1
    try:
        assert res == [250, 250, 8, [[25, 450], [35, 54], [230, 220]]]
        print(f"TEST {i} PASSED")
    except:
        print(f"TEST {i} FAILED")
    finally:
        i += 1
    data = "1;25:10;10;20:230#30:32#230:220"
    res = update_data(data)
    print(res)
    try:
        assert res == [25, 10, 10, [[20, 230], [30, 32], [230, 220]]]
        print(f"TEST {i} PASSED")
    except:
        print(f"TEST {i} FAILED")
    finally:
        i += 1
    data = "1;25:10;10"
    res = update_data(data)
    print(res)
    try:
        assert res == [25, 10, 10, []]
        print(f"TEST {i} PASSED")
    except:
        print(f"TEST {i} FAILED")
    finally:
        i += 1

def update_data(data):
    elem = data.split(";") # separating data
    elem[1] = elem[1].split(":") # formatting position
    x, y = int(elem[1][0]), int(elem[1][1]) # updating position
    health = int(elem[2]) # updating health
    if len(elem) >= 4:
        bullets = split_bullets(elem[3])
    else:
        bullets = []
    return [x, y, health, bullets]

if __name__ == "__main__":
    test_update_data()