import numpy as np
from PIL import Image
import struct
from scipy.stats import chisquare

class ForensicLSBDetector:
    def __init__(self, image_path):
        self.image_path = image_path
        self.image = Image.open(image_path)
        if self.image.mode != 'RGB': 
            self.image = self.image.convert('RGB')
        
        self.flat_pixels = np.array(self.image).flatten()
        
        # Adaptive chunk size
        total_pixels = len(self.flat_pixels)
        if total_pixels < 100000:
            self.chunk_size = 5000
        elif total_pixels < 1000000:
            self.chunk_size = 10000
        else:
            self.chunk_size = 20000
        
        self.chunks = [
            self.flat_pixels[i:i + self.chunk_size] 
            for i in range(0, len(self.flat_pixels), self.chunk_size)
        ]

    def detect_all(self):
        print(f"\n" + "="*95)
        print(f" BÁO CÁO GIÁM ĐỊNH KỸ THUẬT SỐ: {self.image_path}")
        print("="*95)

        # Thu thập dữ liệu
        drop_res = self.detect_sequential_drop()
        bal_res = self.local_balance_test()
        pe_res = self.check_pe_signature()
        chi_res = self.adaptive_chi_square(drop_res['drop_index'])

        # In thông số
        print(f"{'PHƯƠNG PHÁP':25} | {'THÔNG SỐ ĐO ĐẠC':45} | {'NGƯỠNG'}")
        print("-" * 95)
        
        # Sequential Drop
        drop_status = "🚨" if drop_res['suspicious'] else "  "
        print(f"{drop_status} Sequential Drop    | "
              f"MaxDrop={drop_res['max_val']:.4f} @ Chunk {drop_res['drop_index']:4d} "
              f"({drop_res['capacity']:.1f}%)    | > 0.1000")
        
        # Local Balance (IMPROVED)
        bal_status = "🚨" if bal_res['suspicious'] else "  "
        print(f"{bal_status} Local Balance      | "
              f"MeanDev={bal_res['mean_dev']:.4f}, "
              f"UltraBalanced={bal_res['ultra_rate']:.1f}%     | Mean < 0.1")
        
        # Adaptive Chi-Square (IMPROVED)
        chi_status = "🚨" if chi_res['suspicious'] else "  "
        print(f"{chi_status} Adaptive Chi-Sq    | "
              f"NormChi²={chi_res['norm_chi2']:.6f}, "
              f"Balanced={chi_res['balance_ratio']*100:.1f}%    | <0.01 & >60%")
        
        # PE Signature
        pe_status = "🚨" if pe_res['suspicious'] else "  "
        pe_info = f"Found @ Byte {pe_res['found_at']}" if pe_res['suspicious'] else "Not Found"
        print(f"{pe_status} PE Signature       | {pe_info:45} | MZ...PE")

        # Scoring với trọng số
        score = 0
        reasons = []
        
        if pe_res['suspicious']:
            score += 100
            reasons.append("PE executable detected")
        
        if drop_res['suspicious']:
            score += 40
            reasons.append("Sequential boundary detected")
        
        if bal_res['suspicious']:
            score += 20
            reasons.append("Uniform balance across chunks")
        
        if chi_res['suspicious']:
            score += 20
            reasons.append("Pairs too balanced")

        print("-" * 95)
        print(f" TỔNG ĐIỂM NGUY CƠ: {score}/100")
        
        if reasons:
            print(f" LÝ DO:")
            for r in reasons:
                print(f"   • {r}")
        
        if score >= 100:
            verdict = "[!] PHÁT HIỆN MÃ ĐỘC THỰC THI (.EXE)"
        elif score >= 60:
            verdict = "[!] PHÁT HIỆN DỮ LIỆU ẨN CÓ TỔ CHỨC"
        elif score >= 40:
            verdict = "[?] NGHI NGỜ CÓ DỮ LIỆU ẨN"
        else:
            verdict = "[✓] ẢNH AN TOÀN / NHIỄU TỰ NHIÊN"
        
        print(f" KẾT LUẬN: {verdict}")
        print("="*95)
        
        return score

    def local_balance_test(self):
        """Local balance với adaptive threshold (IMPROVED)"""
        devs = []
        for chunk in self.chunks:
            lsb = chunk & 1
            mean_lsb = np.mean(lsb)
            deviation = abs(mean_lsb - 0.5)
            devs.append(deviation)
        
        min_dev = min(devs)
        mean_dev = np.mean(devs)
        std_dev = np.std(devs)
        
        # Count ultra-balanced chunks
        ultra_balanced = sum(1 for d in devs if d < 0.002)
        very_balanced = sum(1 for d in devs if d < 0.01)
        
        ultra_rate = (ultra_balanced / len(self.chunks)) * 100
        very_rate = (very_balanced / len(self.chunks)) * 100
        
        # ADAPTIVE CRITERIA:
        # Stego: Mean deviation thấp + nhiều ultra-balanced chunks
        criteria1 = ultra_rate > 50  # >50% chunks cực kỳ cân bằng
        criteria2 = mean_dev < 0.1 and std_dev < 0.05  # Uniform low deviation
        
        suspicious = criteria1 or criteria2
        
        return {
            'suspicious': suspicious,
            'min_dev': min_dev,
            'mean_dev': mean_dev,
            'std_dev': std_dev,
            'ultra_rate': ultra_rate,
            'very_rate': very_rate
        }

    def detect_sequential_drop(self):
        """Sequential drop detection (giữ nguyên - tốt rồi!)"""
        entropies = []
        for chunk in self.chunks:
            p = np.bincount(chunk & 1, minlength=2) / len(chunk)
            if 0 in p:
                entropies.append(0)
            else:
                entropies.append(-np.sum(p * np.log2(p)))
        
        diffs = [abs(entropies[i] - entropies[i+1]) for i in range(len(entropies)-1)]
        max_val = max(diffs) if diffs else 0
        idx = diffs.index(max_val) if diffs else 0
        
        # Estimate payload capacity
        capacity = (idx / len(self.chunks)) * 100 if self.chunks else 0
        
        return {
            'suspicious': max_val > 0.1,
            'max_val': max_val,
            'drop_index': idx,
            'capacity': capacity
        }

    def adaptive_chi_square(self, drop_idx):
        """Chi-square với normalized metric (IMPROVED)"""
        # Limit sample size
        max_sample = 50000
        sample_end = min((drop_idx + 1) * self.chunk_size, len(self.flat_pixels))
        sample = self.flat_pixels[:sample_end]
        
        # Random sampling if too large
        if len(sample) > max_sample:
            sample = np.random.choice(sample, max_sample, replace=False)
        
        if len(sample) < 1000:
            return {
                'suspicious': False,
                'p_val': 0,
                'norm_chi2': 0,
                'balance_ratio': 0
            }
        
        hist, _ = np.histogram(sample, bins=256, range=(0, 256))
        
        obs, exp = [], []
        pair_diffs = []
        
        for i in range(0, 256, 2):
            y_2i = hist[i]
            y_2i_1 = hist[i+1]
            combined = y_2i + y_2i_1
            
            if combined > 10:
                obs.extend([y_2i, y_2i_1])
                exp.extend([combined/2, combined/2])
                
                # Pair difference ratio
                diff_ratio = abs(y_2i - y_2i_1) / combined if combined > 0 else 0
                pair_diffs.append(diff_ratio)
        
        if not obs:
            return {
                'suspicious': False,
                'p_val': 0,
                'norm_chi2': 0,
                'balance_ratio': 0
            }
        
        chi2_stat, p_val = chisquare(obs, exp)
        
        # Normalized metric
        total_obs = sum(obs)
        norm_chi2 = chi2_stat / total_obs if total_obs > 0 else 0
        
        # Balance ratio
        balanced_pairs = sum(1 for d in pair_diffs if d < 0.05)
        balance_ratio = balanced_pairs / len(pair_diffs) if pair_diffs else 0
        
        # Detection: Low chi-square AND high balance ratio
        suspicious = norm_chi2 < 0.01 and balance_ratio > 0.60
        
        return {
            'suspicious': suspicious,
            'p_val': p_val,
            'norm_chi2': norm_chi2,
            'balance_ratio': balance_ratio
        }

    def check_pe_signature(self):
        """PE signature detection (giữ nguyên - hoàn hảo!)"""
        ext = np.packbits(self.flat_pixels[:200000] & 1).tobytes()
        idx = ext.find(b'MZ')
        
        if idx != -1:
            try:
                pe_ptr = struct.unpack('<I', ext[idx+0x3C:idx+0x40])[0]
                if ext[idx+pe_ptr:idx+pe_ptr+4] == b'PE\0\0':
                    return {'suspicious': True, 'found_at': idx}
            except:
                pass
        
        return {'suspicious': False, 'found_at': None}


if __name__ == "__main__":
    test_images = ['haha.png', 'haha_with_malware.png']
    
    for img in test_images:
        try:
            detector = ForensicLSBDetector(img)
            detector.detect_all()
        except Exception as e:
            print(f"Lỗi khi quét {img}: {e}")