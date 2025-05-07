**文件结构的大致分析**
[相关游戏文件（密a0rx）](https://wwep.lanzoul.com/iZ7Ga2uzy2cb)

DATA内的QPI和QPK一一对应，QPI应该是记录QPK封包内文件偏移位和偏移量的，QPK内多数文件是CZL头的zlib压缩数据

IDX文件夹下的HKT文件疑似记录了QPI的相应读取结构和QPK封包内文件更详细的文件名（较为明显的字符串已提取到[string_in_HKT](string_in_HKT.txt)），但是不知道如何确定HKT内相应偏移量及其对应QPK内具体文件数据

在eboot中HKT的引用在sub_81009EAA内（可能相关的计算函数sub_8100AA02、sub_810937CE和sub_8109A8BC），流程似乎是将HKT内容读入解析后再读取解析各个QPI和QPK封包，先读完所有QPI再读取所有QPK

在sub_81009EAA结束后sub_8100A1EA开始读取解析sys.hdg(在HOTDOG封包内的一个小封包)



**目前可用的工具**

kurrimu对 心之国的爱丽丝 的[相关插件脚本](https://github.com/IcySon55/Kuriimu/issues/518)

Garbro早期对psp上同引擎的[分析](https://github.com/crskycode/GARbro/blob/master/ArcFormats/Psp/ArcQPK.cs)，可以直接使用解包

自己基于上述制作的QPK解包[py脚本](https://github.com/lzhhzl/about-qoo/blob/master/qpk_qpi.py)



**关于对HKT、QPI和QPK文件的进一步分析**

*以下都按偏移量为0x04的小端数据进行分析*

- HKT内
  - 0x00-0x3F 为某些头部信息
  - 0x40-0x40F 为 全FF 间隔
  - 0x410-0x13CEF 疑似为各种偏移相关信息，含有有规律的间隔特征
  - 0x13CF0-0x264C7 含有一些疑似指令和QPK封包内的相关文件名的字符串，似乎是以 "PACK\_封包名_TOP" 开始记述各个封包文件

- QPI内
  - 0x04-0x07 猜测是封入的文件数量count，可能包括了开头和结尾的padding，总是比实际文件数大
  - 0x08-0x0F 不论哪个QPI/QPK都是 07 E3 06 0D 14 05 25 00，可能是版本号或者是特征信息
  - 0x10-0x13  0x00 block
  - 0x14开始 多个offset-size，开头有若干个由 14 00 00 00（offset） 和 00 00 00 80 (size，实则空文件）组成的疑似padding，生成数量为止，直至某一位开始offset为 00 08 00 00，即QPK封包内第一个文件的起始偏移位，有效文件的offset-size形式为 "偏移位(0x04) 偏移量(0x04，需要偏移量&0x3FFFFFFF才能得到文件实际偏移量)"
  - 读取完所有有效文件后，结尾会有少数形式为 "xx xx xx xx(0x04，QPK文件大小) 00 00 00 80" 的数据块，疑似也是一种padding，而最后一个数据块始终是 "xx xx xx xx(0x04，QPK文件大小) 00 00 00 00"
  - 依据HKT内记录的字符串可找到相应封包内的文件名，以此计算实际文件数

- QPK内
  - 0x04-0x07 与相应QPI数据一致
  
  - 0x08-0x0F 和相应QPI一致，这一段都是 07 E3 06 0D 14 05 25 00
  
  - 0x10-0x7FF 类似padding一样的 全00 间隔，间隔确保封包内第一个文件都是从0x800开始存储，之后各个封包内文件数据间用若干个 全00 间隔

- QPK封包内的CZL
  - 0x04-0x07 CZL压缩数据的偏移量
  - 0x08-0x0B 未知
  - 0xC-(0xC+CZL压缩数据的偏移量&0x3FFFFFFF) Zlib压缩数据
  

**其他未完全解明的文件结构**

- AKB文件，在KS.QPK中的首个文件(名为kslist.akb)

- GOF 字库文件 已放在font文件夹下，其中含有非等宽的无压缩字形的tile

- HOTDOG封包内的HDG文件
疑似也是一种封包，里面含有若干个CZL文件(疑似为TGA图像)
  - 0x4-0xB 未知
  - 0x0C-0x53F 偏移信息
  - 从0x0C开始记述第一个CZL的偏移位（0xC-0xF,共0x04），且之后疑似跟着偏移量（0x10-0x13,共0x04）,实际偏移量貌似和QPI中的算法一样（偏移量&0x3FFFFFFF）
  - 之后每间隔0x0C就有下一个偏移位 偏移量，但间隔数据不太一致，猜测间隔数据第一位有可能是文件名的偏移量
  - 偏移信息最后的偏移位（0x520-0x523）为HDG封包所有文件名的记述，用 这个偏移位 依次+ 每个间隔数据第一位 似乎能得到各个封包文件对应的文件名的偏移位

**各个封包大致所含的文件种类**

BGM、SE、VOICE 顾名思义，音频文件

CHARA 人物立绘相关，HOTDOG、TGA 其他图片文件（格式为tga）

CSV 部分数值、文本的表，KS 文本（类kag脚本）

OTHER 杂项，MOVIE 顾名思义，HAM 不知道
