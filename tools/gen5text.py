import code 
import io
import math
import struct, re
import os
import json
import codecs
import sys
from binary16 import binaryreader, binarywriter

def read16(stream):
	return int.from_bytes(stream.read(2), 'little')

def read32(stream):
	return int.from_bytes(stream.read(4), 'little')

def gen5get(f):
    texts = []
    reader = binaryreader(f)
    
    numblocks = reader.read16()
    numentries = reader.read16()
    filesize = reader.read32()
    zero = reader.read32()
    blockoffsets = []


    for i in range(numblocks):
        blockoffsets.append(reader.read32())
    # filesize == len(f)-reader.pos()
    for i in range(numblocks):
        reader.seek(blockoffsets[i])
        size = reader.read32()
        tableoffsets = []
        charcounts = []
        textflags = []
        initial_key = 0
        for j in range(numentries):
            tableoffsets.append(reader.read32())
            charcounts.append(reader.read16())
            textflags.append(reader.read16())
        for j in range(numentries):
            compressed = False
            encchars = []
            text = ""
            reader.seek(blockoffsets[i]+tableoffsets[j])
            for k in range(charcounts[j]):
                encchars.append(reader.read16())
            key = encchars[len(encchars)-1]^0xFFFF
            initial_key = encchars[len(encchars)-1]
            decchars = []
            
            while encchars:
                encoded = encchars.pop()
                char = encoded ^ key
                key = ((key>>3)|(key<<13))&0xFFFF
                decchars.insert(0, char)
            
            if decchars[0] == 0xF100:
                compressed = True
                decchars.pop(0)
                newstring = []
                container = 0
                bit = 0
                while decchars:
                    container |= decchars.pop(0)<<bit
                    bit += 16
                    while bit >= 9:
                        bit -= 9
                        c = container&0x1FF
                        if c == 0x1FF:
                            newstring.append(0xFFFF)
                        else:
                            newstring.append(c)
                        container >>= 9
                decchars = newstring
            while decchars:
                c = decchars.pop(0)
                if c == 0xFFFF:
                    text += "$"
                elif c == 0xFFFE:
                    text += "\\n"
                elif c == 0xF000:
                    try:
                        kind = decchars.pop(0)
                        count = decchars.pop(0)
                        if kind == 0xbe00 and count == 0:
                            text += "\\f"
                            continue
                        if kind == 0xbe01 and count == 0:
                            text += "\\r"
                            continue
                        text += "VAR("
                        args = [kind]
                        for k in range(count):
                            args.append(decchars.pop(0))
                    except IndexError:
                        break
                    text += ", ".join(map(str, args))
                    text += ")"
                else:
                    text += chr(c)
            e = "%i_%i"%(i, j)
            flag = ""
            val = textflags[j]
            c = 65
            while val:
                if val&1:
                    # print(c)
                    # print(chr(c))
                    flag += chr(c)
                c += 1
                val >>= 1
            if compressed:
                flag += "c"
            e += flag
            texts.append([e, text])
    return texts


def gen5put(texts):
    textofs = {}
    sizes = {}
    comments = {}
    textflags = {}
    blockwriters = {}
    blocksize = {}
    numentries = 0
    Main_key = 0x7C89
    for entry in texts:
        match = re.match("([^_]+)_([0-9]+)(.*)", entry[0])
        if not match:
            continue
        blockid = match.group(1)
        textid = int(match.group(2))
        if textid == 0:
            Main_key = 0x7C89
        flags = match.group(3)
        text = entry[1]
        if blockid.lower() == "comment":
            comments[textid] = text
            continue

        numentries = max(numentries, textid + 1)
        blockid = int(blockid)
        if blockid not in blockwriters:
            blockwriters[blockid] = binarywriter()
            textofs[blockid] = {}
            sizes[blockid] = {}
            blocksize[blockid] = 0
            textflags[blockid] = {}
        textofs[blockid][textid] = blockwriters[blockid].pos()
        dec = []
        while text:
            c = text[0]
            text = text[1:]
            if c == '\\':
                c = text[0]
                text = text[1:]
                if c == 'x':
                    n = int(text[:4], 16)
                    text = text[4:]
                elif c == 'n':
                    n = 0xFFFE
                elif c == 'r':
                    dec.append(0xF000)
                    dec.append(0xbe01)
                    dec.append(0)
                    continue
                elif c == 'f':
                    dec.append(0xF000)
                    dec.append(0xbe00)
                    dec.append(0)
                    continue
                else:
                    n = 1
                dec.append(n)
            elif c == '$':
                dec.append(0xFFFF)
            elif c == 'V':
                if text[:2] == "AR":
                    text = text[3:]
                    eov = text.find(")")
                    args = list(map(int, text[:eov].split(",")))
                    text = text[eov+1:]
                    dec.append(0xF000)
                    dec.append(args.pop(0))
                    dec.append(len(args))
                    for a in args:
                        dec.append(a)
                else:
                    dec.append(ord('V'))
            else:
                dec.append(ord(c))

        key = Main_key
        enc = []
        
        for i in dec:
            char = i ^ key
            key = (key << 3 | key >> 13) & 0xFFFF
            enc.append(char)

        Main_key += 0x2983
        Main_key = Main_key - 0x10000 if Main_key > 0xFFFF else Main_key

        sizes[blockid][textid] = len(enc)
        blocksize[blockid] += len(enc) * 2
        for e in enc:
            blockwriters[blockid].write16(e)
    numblocks = max(blockwriters)+1
    if numblocks != len(blockwriters):
        raise KeyError

    offsets = []
    baseofs = 12+4*numblocks
    textblock = binarywriter()
    for i in range(numblocks):
        data = blockwriters[i].toarray()
        offsets.append(baseofs+textblock.pos())
        relofs = numentries*8+4
        textblock.write32(blocksize[i] + relofs)

        for j in range(numentries):
            textblock.write32(textofs[i][j]+relofs)
            textblock.write16(sizes[i][j])
            textblock.write16(0)
        textblock.writear(data)
    writer = binarywriter()
    writer.write16(numblocks)
    writer.write16(numentries)
    writer.write32(int(textblock.pos() / 2))
    writer.write32(0)
    for i in range(numblocks):
        writer.write32(offsets[i])
    writer.writear(textblock.toarray())
    return writer.tostring()

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("Usage: python gen5text.py [-d|-g] input output")
        sys.exit(1)
    if sys.argv[1] == "-d":
        with open(sys.argv[2], "rb") as files:
            text_dump = gen5get(files.read())
            with codecs.open(sys.argv[3], 'w', encoding='utf_8') as f:
                json.dump(text_dump, f, indent=4, ensure_ascii=False)
    elif sys.argv[1] == "-g":
        with codecs.open(sys.argv[2], 'r', encoding='utf_8') as f:
            texts = json.load(f)
            try: 
                data = gen5put(texts)
            except:
                data = bytes([])
            with open(sys.argv[3], "wb") as newfile:
                newfile.write(data)
