import numpy as np
from PIL import Image
import struct
from scipy.stats import chisquare
import argparse
import sys
import os

class ForensicLSBDetector:
    def __init__(self, image_path):
        self.image_path = image_path
        self.image = Image.open(image_path)
        if self.image.mode != 'RGB': 
            self.image = self.image.convert('RGB')
        
        self.flat_pixels = np.array(self.image).ravel()
        
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

    # ── column widths ──────────────────────────────────────
    _W_FLAG   =  2   # icon / blank
    _W_METHOD = 20   # method name
    _W_PARAMS = 52   # measurement params
    _W_THRESH = 24   # threshold

    @classmethod
    def _row(cls, flag, method, params, threshold):
        """Format one result row with fixed-width columns."""
        flag_s   = str(flag  ).ljust(cls._W_FLAG)
        method_s = str(method).ljust(cls._W_METHOD)
        params_s = str(params).ljust(cls._W_PARAMS)
        thresh_s = str(threshold).ljust(cls._W_THRESH)
        return f"{flag_s} {method_s} | {params_s} | {thresh_s}"

    @classmethod
    def _divider(cls):
        total = cls._W_FLAG + 1 + cls._W_METHOD + 3 + cls._W_PARAMS + 3 + cls._W_THRESH
        return "-" * total

    @classmethod
    def _header(cls):
        return cls._row("", "PHƯƠNG PHÁP", "THÔNG SỐ ĐO ĐẠC", "NGƯỠNG")

    def detect_all(self):
        W = self._W_FLAG + 1 + self._W_METHOD + 3 + self._W_PARAMS + 3 + self._W_THRESH

        print()
        print("=" * W)
        print(f" BÁO CÁO GIÁM ĐỊNH KỸ THUẬT SỐ: {self.image_path}")
        print("=" * W)

        drop_res = self.detect_sequential_drop()
        bal_res  = self.local_balance_test()
        pe_res   = self.check_pe_signature()
        chi_res  = self.adaptive_chi_square(drop_res['drop_index'])

        print(self._header())
        print(self._divider())

        # Sequential Drop
        drop_flag = "🚨" if drop_res['suspicious'] else "  "
        drop_params = (
            f"MaxDrop={drop_res['max_val']:.4f} "
            f"@ Chunk {drop_res['drop_index']:4d} "
            f"({drop_res['capacity']:5.1f}%)"
        )
        print(self._row(drop_flag, "Sequential Drop", drop_params, "> 0.1000"))

        # Local Balance
        bal_flag = "🚨" if bal_res['suspicious'] else "  "
        bal_params = (
            f"MeanDev={bal_res['mean_dev']:.4f}  "
            f"StdDev={bal_res['std_dev']:.4f}  "
            f"Ultra={bal_res['ultra_rate']:5.1f}%"
        )
        print(self._row(bal_flag, "Local Balance", bal_params, "(<0.1 & <0.05) or >50%"))

        # Adaptive Chi-Square
        chi_flag = "🚨" if chi_res['suspicious'] else "  "
        chi_params = (
            f"NormChi²={chi_res['norm_chi2']:.6f}  "
            f"Balanced={chi_res['balance_ratio']*100:5.1f}%"
        )
        print(self._row(chi_flag, "Adaptive Chi-Sq", chi_params, "<0.01 & >60%"))

        # PE Signature
        pe_flag = "🚨" if pe_res['suspicious'] else "  "
        pe_params = (
            f"Found @ Byte {pe_res['found_at']}" if pe_res['suspicious'] else "Not Found"
        )
        print(self._row(pe_flag, "PE Signature", pe_params, "MZ...PE"))

        # ── Scoring ──────────────────────────────────────────
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

        print(self._divider())
        print(f" TỔNG ĐIỂM NGUY CƠ : {score}")
        
        if reasons:
            print(f" LÝ DO             :")
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
        
        print(f" KẾT LUẬN          : {verdict}")
        print("=" * W)
        
        return score

    def local_balance_test(self):
        devs = []
        for chunk in self.chunks:
            lsb = chunk & 1
            mean_lsb = np.mean(lsb)
            deviation = abs(mean_lsb - 0.5)
            devs.append(deviation)
        
        min_dev  = min(devs)
        mean_dev = np.mean(devs)
        std_dev  = np.std(devs)
        
        ultra_balanced = sum(1 for d in devs if d < 0.002)
        very_balanced  = sum(1 for d in devs if d < 0.01)
        
        ultra_rate = (ultra_balanced / len(self.chunks)) * 100
        very_rate  = (very_balanced  / len(self.chunks)) * 100
        
        criteria1 = ultra_rate > 50
        criteria2 = mean_dev < 0.1 and std_dev < 0.05
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
        capacity = (idx / len(self.chunks)) * 100 if self.chunks else 0
        
        return {
            'suspicious': max_val > 0.1,
            'max_val': max_val,
            'drop_index': idx,
            'capacity': capacity
        }

    def adaptive_chi_square(self, drop_idx):
        max_sample = 50000
        sample_end = min((drop_idx + 1) * self.chunk_size, len(self.flat_pixels))
        sample = self.flat_pixels[:sample_end]
        if len(sample) > max_sample:
            step = len(sample) // max_sample
            sample = sample[::step][:max_sample]
        
        if len(sample) < 1000:
            return {'suspicious': False, 'p_val': 0, 'norm_chi2': 0, 'balance_ratio': 0}
        
        hist, _ = np.histogram(sample, bins=256, range=(0, 256))
        obs, exp, pair_diffs = [], [], []
        
        for i in range(0, 256, 2):
            y_2i   = hist[i]
            y_2i_1 = hist[i+1]
            combined = y_2i + y_2i_1
            if combined > 10:
                obs.extend([y_2i, y_2i_1])
                exp.extend([combined/2, combined/2])
                diff_ratio = abs(y_2i - y_2i_1) / combined if combined > 0 else 0
                pair_diffs.append(diff_ratio)
        
        if not obs:
            return {'suspicious': False, 'p_val': 0, 'norm_chi2': 0, 'balance_ratio': 0}
        
        chi2_stat, p_val = chisquare(obs, exp)
        total_obs = sum(obs)
        norm_chi2 = chi2_stat / total_obs if total_obs > 0 else 0
        balanced_pairs = sum(1 for d in pair_diffs if d < 0.05)
        balance_ratio  = balanced_pairs / len(pair_diffs) if pair_diffs else 0
        suspicious = norm_chi2 < 0.01 and balance_ratio > 0.60
        
        return {
            'suspicious': suspicious,
            'p_val': p_val,
            'norm_chi2': norm_chi2,
            'balance_ratio': balance_ratio
        }

    def check_pe_signature(self):
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


# ─────────────────────────────────────────────
#  CLI Entry Point
# ─────────────────────────────────────────────
def build_parser():
    parser = argparse.ArgumentParser(
        prog="forensic_lsb_detector",
        description="🔍 Phát hiện mã độc / dữ liệu ẩn trong ảnh bằng phân tích LSB",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""Ví dụ sử dụng:
  python forensic_lsb_detector.py image.png
  python forensic_lsb_detector.py image1.jpg image2.png image3.bmp
  python forensic_lsb_detector.py *.png
        """
    )
    parser.add_argument(
        "images",
        nargs="+",
        metavar="IMAGE",
        help="Đường dẫn tới file ảnh cần kiểm tra (hỗ trợ nhiều file)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Hiện thêm thông tin chi tiết khi quét"
    )
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    total = len(args.images)
    passed = 0
    flagged = 0

    for img_path in args.images:
        if not os.path.isfile(img_path):
            print(f"[✗] Không tìm thấy file: {img_path}")
            continue
        
        try:
            detector = ForensicLSBDetector(img_path)
            score = detector.detect_all()

            if score >= 40:
                flagged += 1
            else:
                passed += 1

        except Exception as e:
            print(f"[✗] Lỗi khi quét '{img_path}': {e}")

    # Tóm tắt nếu quét nhiều file
    if total > 1:
        sep = "─" * 50
        print(f"\n{sep}")
        print(f" TỔNG KẾT : {total} file  |  ✅ An toàn: {passed}  |  🚨 Nghi ngờ/Độc hại: {flagged}")
        print(f"{sep}\n")

    sys.exit(1 if flagged > 0 else 0)


if __name__ == "__main__":
    main()
