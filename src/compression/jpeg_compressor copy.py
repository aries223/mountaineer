from .base_compressor import BaseCompressor

class JpegCompressor(BaseCompressor):
    def __init__(self):
        super().__init__()

    def compress_file(self, input_path, output_path=None, lossless=False,
                     strip_metadata=False, jpeg_quality=None):
        if jpeg_quality is None:
            raise ValueError("jpeg_quality must be provided")

        cmd = ["jpegoptim"]

        if not lossless:
            # Use custom compression level from preferences
            cmd.append(f"-m{int(jpeg_quality)}")

        if strip_metadata:
            cmd.append("--strip-all")

        if output_path and output_path != input_path:
            cmd.extend(["--dest", output_path])

        cmd.append(input_path)

        return self.run_command(cmd)