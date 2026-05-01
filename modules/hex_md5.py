def hex_md5(string, ver=None):
    """
    模拟JavaScript的MD5加密实现
    :param string: 需要加密的字符串
    :param ver: 版本号，当为"1.8"时不添加后缀
    :return: 返回32位小写MD5值
    """
    def md5_RotateLeft(lValue, iShiftBits):
        """位运算左移，模拟JavaScript的位运算"""
        return (lValue << iShiftBits) | (lValue >> (32 - iShiftBits))

    def md5_AddUnsigned(lX, lY):
        """模拟JavaScript的无符号整数加法"""
        lX4 = lX & 0x40000000
        lY4 = lY & 0x40000000
        lX8 = lX & 0x80000000
        lY8 = lY & 0x80000000
        lResult = (lX & 0x3FFFFFFF) + (lY & 0x3FFFFFFF)
        if lX4 & lY4:
            return lResult ^ 0x80000000 ^ lX8 ^ lY8
        if lX4 | lY4:
            if lResult & 0x40000000:
                return lResult ^ 0xC0000000 ^ lX8 ^ lY8
            else:
                return lResult ^ 0x40000000 ^ lX8 ^ lY8
        else:
            return lResult ^ lX8 ^ lY8

    # MD5的四个基本运算函数
    def md5_F(x, y, z): return (x & y) | ((~x) & z)
    def md5_G(x, y, z): return (x & z) | (y & (~z))
    def md5_H(x, y, z): return x ^ y ^ z
    def md5_I(x, y, z): return y ^ (x | (~z))

    # MD5的四轮运算
    def md5_FF(a, b, c, d, x, s, ac):
        """第一轮"""
        a = md5_AddUnsigned(a, md5_AddUnsigned(md5_AddUnsigned(md5_F(b, c, d), x), ac))
        return md5_AddUnsigned(md5_RotateLeft(a, s), b)

    def md5_GG(a, b, c, d, x, s, ac):
        """第二轮"""
        a = md5_AddUnsigned(a, md5_AddUnsigned(md5_AddUnsigned(md5_G(b, c, d), x), ac))
        return md5_AddUnsigned(md5_RotateLeft(a, s), b)

    def md5_HH(a, b, c, d, x, s, ac):
        """第三轮"""
        a = md5_AddUnsigned(a, md5_AddUnsigned(md5_AddUnsigned(md5_H(b, c, d), x), ac))
        return md5_AddUnsigned(md5_RotateLeft(a, s), b)

    def md5_II(a, b, c, d, x, s, ac):
        """第四轮"""
        a = md5_AddUnsigned(a, md5_AddUnsigned(md5_AddUnsigned(md5_I(b, c, d), x), ac))
        return md5_AddUnsigned(md5_RotateLeft(a, s), b)

    def md5_ConvertToWordArray(string):
        """
        将字符串转换为字数组
        这里直接使用字符ASCII值，不进行UTF8编码
        """
        lMessageLength = len(string)
        lNumberOfWords_temp1 = lMessageLength + 8
        lNumberOfWords_temp2 = (lNumberOfWords_temp1 - (lNumberOfWords_temp1 % 64)) // 64
        lNumberOfWords = (lNumberOfWords_temp2 + 1) * 16
        lWordArray = [0] * lNumberOfWords
        
        # 处理每个字符
        for lByteCount in range(lMessageLength):
            lWordCount = (lByteCount - (lByteCount % 4)) // 4
            lBytePosition = (lByteCount % 4) * 8
            # 直接使用字符的ASCII值
            lWordArray[lWordCount] = lWordArray[lWordCount] | (ord(string[lByteCount]) << lBytePosition)
        
        # 添加填充位
        lWordCount = (lMessageLength - (lMessageLength % 4)) // 4
        lBytePosition = (lMessageLength % 4) * 8
        lWordArray[lWordCount] = lWordArray[lWordCount] | (0x80 << lBytePosition)
        lWordArray[lNumberOfWords - 2] = lMessageLength << 3
        lWordArray[lNumberOfWords - 1] = lMessageLength >> 29
        return lWordArray

    def md5_WordToHex(lValue):
        """将32位数值转换为16进制字符串"""
        WordToHexValue = ""
        for lCount in range(4):
            lByte = (lValue >> (lCount * 8)) & 255
            WordToHexValue += format(lByte, '02x')
        return WordToHexValue

    # 处理版本和后缀
    # 如果不是1.8版本，添加{Urp602019}后缀
    if ver != "1.8":
        string = string + "{Urp602019}"
    
    # 初始化MD5运算的常量
    x = md5_ConvertToWordArray(string)
    a = 0x67452301  # A
    b = 0xEFCDAB89  # B
    c = 0x98BADCFE  # C
    d = 0x10325476  # D

    # MD5的主循环
    for k in range(0, len(x), 16):
        AA, BB, CC, DD = a, b, c, d
        a = md5_FF(a, b, c, d, x[k + 0], 7, 0xD76AA478)
        d = md5_FF(d, a, b, c, x[k + 1], 12, 0xE8C7B756)
        c = md5_FF(c, d, a, b, x[k + 2], 17, 0x242070DB)
        b = md5_FF(b, c, d, a, x[k + 3], 22, 0xC1BDCEEE)
        a = md5_FF(a, b, c, d, x[k + 4], 7, 0xF57C0FAF)
        d = md5_FF(d, a, b, c, x[k + 5], 12, 0x4787C62A)
        c = md5_FF(c, d, a, b, x[k + 6], 17, 0xA8304613)
        b = md5_FF(b, c, d, a, x[k + 7], 22, 0xFD469501)
        a = md5_FF(a, b, c, d, x[k + 8], 7, 0x698098D8)
        d = md5_FF(d, a, b, c, x[k + 9], 12, 0x8B44F7AF)
        c = md5_FF(c, d, a, b, x[k + 10], 17, 0xFFFF5BB1)
        b = md5_FF(b, c, d, a, x[k + 11], 22, 0x895CD7BE)
        a = md5_FF(a, b, c, d, x[k + 12], 7, 0x6B901122)
        d = md5_FF(d, a, b, c, x[k + 13], 12, 0xFD987193)
        c = md5_FF(c, d, a, b, x[k + 14], 17, 0xA679438E)
        b = md5_FF(b, c, d, a, x[k + 15], 22, 0x49B40821)
        a = md5_GG(a, b, c, d, x[k + 1], 5, 0xF61E2562)
        d = md5_GG(d, a, b, c, x[k + 6], 9, 0xC040B340)
        c = md5_GG(c, d, a, b, x[k + 11], 14, 0x265E5A51)
        b = md5_GG(b, c, d, a, x[k + 0], 20, 0xE9B6C7AA)
        a = md5_GG(a, b, c, d, x[k + 5], 5, 0xD62F105D)
        d = md5_GG(d, a, b, c, x[k + 10], 9, 0x2441453)
        c = md5_GG(c, d, a, b, x[k + 15], 14, 0xD8A1E681)
        b = md5_GG(b, c, d, a, x[k + 4], 20, 0xE7D3FBC8)
        a = md5_GG(a, b, c, d, x[k + 9], 5, 0x21E1CDE6)
        d = md5_GG(d, a, b, c, x[k + 14], 9, 0xC33707D6)
        c = md5_GG(c, d, a, b, x[k + 3], 14, 0xF4D50D87)
        b = md5_GG(b, c, d, a, x[k + 8], 20, 0x455A14ED)
        a = md5_GG(a, b, c, d, x[k + 13], 5, 0xA9E3E905)
        d = md5_GG(d, a, b, c, x[k + 2], 9, 0xFCEFA3F8)
        c = md5_GG(c, d, a, b, x[k + 7], 14, 0x676F02D9)
        b = md5_GG(b, c, d, a, x[k + 12], 20, 0x8D2A4C8A)
        a = md5_HH(a, b, c, d, x[k + 5], 4, 0xFFFA3942)
        d = md5_HH(d, a, b, c, x[k + 8], 11, 0x8771F681)
        c = md5_HH(c, d, a, b, x[k + 11], 16, 0x6D9D6122)
        b = md5_HH(b, c, d, a, x[k + 14], 23, 0xFDE5380C)
        a = md5_HH(a, b, c, d, x[k + 1], 4, 0xA4BEEA44)
        d = md5_HH(d, a, b, c, x[k + 4], 11, 0x4BDECFA9)
        c = md5_HH(c, d, a, b, x[k + 7], 16, 0xF6BB4B60)
        b = md5_HH(b, c, d, a, x[k + 10], 23, 0xBEBFBC70)
        a = md5_HH(a, b, c, d, x[k + 13], 4, 0x289B7EC6)
        d = md5_HH(d, a, b, c, x[k + 0], 11, 0xEAA127FA)
        c = md5_HH(c, d, a, b, x[k + 3], 16, 0xD4EF3085)
        b = md5_HH(b, c, d, a, x[k + 6], 23, 0x4881D05)
        a = md5_HH(a, b, c, d, x[k + 9], 4, 0xD9D4D039)
        d = md5_HH(d, a, b, c, x[k + 12], 11, 0xE6DB99E5)
        c = md5_HH(c, d, a, b, x[k + 15], 16, 0x1FA27CF8)
        b = md5_HH(b, c, d, a, x[k + 2], 23, 0xC4AC5665)
        a = md5_II(a, b, c, d, x[k + 0], 6, 0xF4292244)
        d = md5_II(d, a, b, c, x[k + 7], 10, 0x432AFF97)
        c = md5_II(c, d, a, b, x[k + 14], 15, 0xAB9423A7)
        b = md5_II(b, c, d, a, x[k + 5], 21, 0xFC93A039)
        a = md5_II(a, b, c, d, x[k + 12], 6, 0x655B59C3)
        d = md5_II(d, a, b, c, x[k + 3], 10, 0x8F0CCC92)
        c = md5_II(c, d, a, b, x[k + 10], 15, 0xFFEFF47D)
        b = md5_II(b, c, d, a, x[k + 1], 21, 0x85845DD1)
        a = md5_II(a, b, c, d, x[k + 8], 6, 0x6FA87E4F)
        d = md5_II(d, a, b, c, x[k + 15], 10, 0xFE2CE6E0)
        c = md5_II(c, d, a, b, x[k + 6], 15, 0xA3014314)
        b = md5_II(b, c, d, a, x[k + 13], 21, 0x4E0811A1)
        a = md5_II(a, b, c, d, x[k + 4], 6, 0xF7537E82)
        d = md5_II(d, a, b, c, x[k + 11], 10, 0xBD3AF235)
        c = md5_II(c, d, a, b, x[k + 2], 15, 0x2AD7D2BB)
        b = md5_II(b, c, d, a, x[k + 9], 21, 0xEB86D391)
        a = md5_AddUnsigned(a, AA)
        b = md5_AddUnsigned(b, BB)
        c = md5_AddUnsigned(c, CC)
        d = md5_AddUnsigned(d, DD)

    # 返回最终的MD5值（32位小写）
    return (md5_WordToHex(a) + md5_WordToHex(b) + md5_WordToHex(c) + md5_WordToHex(d)).lower()