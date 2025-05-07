import os
import struct
import zlib

def main():
    # 设置当前工作目录为脚本所在的目录
    current_script_path = r"D:\Program\qoo"  # change work dir here
    os.chdir(current_script_path)
    
    file = "GOF"  # change pack name here
    qpi_path = file + ".QPI"
    qpk_path = file + ".QPK"
    
    with open(qpi_path, 'rb') as qpi:
        br = qpi.read()
        
        # 读取文件头（4 字节）
        header = br[:4]
        print(header.decode('ascii'))
        
        # 读取文件数量（4 字节）
        count = struct.unpack('<I', br[4:8])[0]  # 该数量涵盖了若干个开头和结尾偏移量为 0x80(小端位00000080) 的offset-size(可能是padding)
        print(f"File Count: {count}")
        
        # 0x08-0x0F maybe version
        # 0x10-0x13 0x00 block
        br = br[0x14:]  # offset-size start
        
        # IN QPK file, magic(0x00-0x03) count(0x04-0x07) version(0x08-0x0F)
        # After 0x10-0x7FF block(size 0x7F0), then first file start-offset(0x800)
        with open(qpk_path, 'rb') as qpk:
            br2 = qpk.read()
            
            for i in range(count):
                # 读取偏移量（4 字节）
                offset = struct.unpack('<I', br[:4])[0]
                br = br[4:]
                # 读取大小（4 字节）
                size = struct.unpack('<I', br[:4])[0]
                br = br[4:]
                # 其他参数
                isCZL = False
                ext = ".qfi"
                
                if (size & 0x80000000) >> 31 == 1:  # Empty File空文件
                    # print("Empty File")
                    continue
                elif (size & 0x40000000) >> 30 == 1:  # Compressed File压缩文件
                    if br2[offset:offset+4].decode('ascii') == "CZL\x00":
                        ext = ".czl"
                        isCZL = True
                else:  # 尝试获取 RIFF 头部
                    if br2[offset:offset+4].decode('ascii') == "RIFF":
                        ext = ".at3"
                
                print(f"{i:04d}{ext}")
                print(f"Offset: {offset:02X}")
                print(f"Size: {(size & 0x3FFFFFFF):02X}",end='\n\n')
                
                # 创建输出目录（如果不存在）
                output_dir = "output"
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)
                
                output_path = os.path.join(output_dir, f"{i:04d}{ext}")
                
                with open(output_path, 'wb') as bw:
                    if isCZL:
                        # 读取压缩数据的大小（4 字节）
                        size = struct.unpack('<I',br2[offset+0x4:offset+0x4+4])[0]
                        cSize = (size & 0x3FFFFFFF)
                        size += 0xC
                        
                        # 解压缩 CZL 文件
                        decompressed_data = zlib.decompress(br2[offset+0xC:offset+0xC+cSize])
                        
                        # 保存解压缩后的数据
                        unc_output_path = os.path.join(output_dir, f"{i:04d}{ext}.unc")
                        with open(unc_output_path, 'wb') as bw2:
                            bw2.write(decompressed_data)
                    # 写入普通文件数据
                    bw.write(br2[offset:offset+int(size & 0x3FFFFFFF)])

if __name__ == "__main__":
    main()