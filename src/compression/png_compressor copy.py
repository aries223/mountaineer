from .base_compressor import BaseCompressor

class PngCompressor(BaseCompressor):
    def __init__(self):
        super().__init__()

    def compress_file(self, input_path, output_path=None, lossless=False,
                     strip_metadata=False, png_quality=None):
        if png_quality is None:
            raise ValueError("png_quality must be provided")

        if lossless:
            # Lossless compression - just use oxipng with max optimization
            cmd = ["oxipng", "--opt=max", input_path]
            success = self.run_command(cmd)
            return success
        else:
            # Non-lossless compression - use pngquant first
            pngquant_cmd = ["pngquant", f"-Q{int(png_quality)}", "--ext", ".png", "--force"]
            pngquant_cmd.append(input_path)
            success = self.run_command(pngquant_cmd)
            if not success:
                return False

        # If strip metadata is enabled, run oxipng with strip flag
        if strip_metadata:
            cmd = ["oxipng", "--opt=max", "--strip=all", input_path]
            return self.run_command(cmd)

        return True  # Return success for non-strip case
