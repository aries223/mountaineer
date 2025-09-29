from .base_compressor import BaseCompressor

class PngCompressor(BaseCompressor):
    def __init__(self):
        super().__init__()

    def compress_file(self, input_path, output_path=None, lossless=False,
                     strip_metadata=False, png_quality=None, is_rgba=False):
        cmd = ["oxipng"]

        if lossless:
            # Lossless (long time, not recommended)
            cmd.extend(["-omax", "-Z", "--fast"])
        else:
            # Default normal compression
            if png_quality is None:
                raise ValueError("png_quality must be provided for non-lossless compression")
            cmd.extend([f"-o{int(png_quality)}", "-f", "0-9"])

        if strip_metadata:
            cmd.append("--strip=all")

        if is_rgba:
            cmd.append("-a")

        if output_path and output_path != input_path:
            cmd.extend(["--out", output_path])

        cmd.append(input_path)

        return self.run_command(cmd)
