import cv2
import numpy as np

# ------------- Parameter Fields -------------
params = {
    "width": 1920,
    "height": 1080,
    "gradient_top": 75,         # Top value of vertical gradient (lighter)
    "gradient_bottom": 50,      # Bottom value of vertical gradient (darker)
    
    # First mountain curve parameters
    "sine_amplitude1": 80,      # Amplitude for first mountain curve
    "sine_frequency1": 2 * np.pi,  # Frequency multiplier for first mountain curve
    "noise_std1": 5,            # Noise standard deviation for first mountain curve
    
    # Second mountain curve parameters
    "sine_amplitude2": 40,      # Amplitude for second mountain curve
    "sine_frequency2": 4 * np.pi,  # Frequency multiplier for second mountain curve
    "phase_offset2": 1,         # Phase offset for second mountain curve
    "noise_std2": 5,            # Noise standard deviation for second mountain curve
    
    "gaussian_blur_mask_kernel": 101,  # Kernel size for heavy blur on mountain masks (must be odd)
    "gaussian_blur_final_kernel": 31,  # Kernel size for final smoothing blur (must be odd)
    "mountain_contrast_multiplier": 1.2,  # Contrast boost for mountain layer
    "blend_weight_gradient": 0.4,  # Weight for the gradient background during blending
    "blend_weight_mountain": 0.6,  # Weight for the mountain layer during blending
    "random_noise_threshold": 0.95, # Threshold for adding random noise mountain blobs (0-1 probability)
}
# ------------- End Parameter Fields -------------

width = params["width"]
height = params["height"]

# Create a base vertical gradient background (top = gradient_top, bottom = gradient_bottom)
gradient = np.tile(
    np.linspace(params["gradient_top"], params["gradient_bottom"], height, dtype=np.uint8)[:, None],
    (1, width)
)

# Create empty masks for two mountain silhouettes
mask1 = np.zeros((height, width), dtype=np.uint8)
mask2 = np.zeros((height, width), dtype=np.uint8)

# Generate the first mountain curve using a sine wave with slight noise
x = np.arange(width)
np.random.seed(42)  # For reproducibility
mountain_curve1 = (
    height * 0.5 +
    params["sine_amplitude1"] * np.sin(params["sine_frequency1"] * x / width) +
    np.random.normal(0, params["noise_std1"], width)
).astype(np.int32)
mountain_curve1 = np.clip(mountain_curve1, 0, height - 1)

# Generate the second mountain curve with higher frequency and a phase offset
mountain_curve2 = (
    height * 0.6 +
    params["sine_amplitude2"] * np.sin(params["sine_frequency2"] * x / width + params["phase_offset2"]) +
    np.random.normal(0, params["noise_std2"], width)
).astype(np.int32)
mountain_curve2 = np.clip(mountain_curve2, 0, height - 1)

# Fill mask1 from mountain_curve1 downward (mountain area is white)
for i in range(width):
    mask1[mountain_curve1[i]:, i] = 255

# Fill mask2 from mountain_curve2 downward (mountain area is white)
for i in range(width):
    mask2[mountain_curve2[i]:, i] = 255

# Combine the two masks to include both mountain silhouettes
combined_mask = cv2.max(mask1, mask2)

# Optionally, add a few random mountain-like blobs for extra variety
random_noise = (np.random.rand(height, width) > params["random_noise_threshold"]).astype(np.uint8) * 255
combined_mask = cv2.max(combined_mask, random_noise)

# Apply a heavy Gaussian blur to the combined mask for very smooth transitions
mask_blurred = cv2.GaussianBlur(combined_mask, 
                                (params["gaussian_blur_mask_kernel"], params["gaussian_blur_mask_kernel"]),
                                0)

# Normalize the blurred mask to a 0.0 - 1.0 range
mask_normalized = mask_blurred.astype(np.float32) / 255.0

# Create a mountain layer:
# Map mask values so that 0 becomes gradient_bottom and 1 becomes gradient_top.
# Boost contrast with the contrast multiplier and clip to remain within [gradient_bottom, gradient_top].
mountain_layer = params["gradient_bottom"] + np.clip(
    mask_normalized * (params["gradient_top"] - params["gradient_bottom"]) * params["mountain_contrast_multiplier"],
    0, params["gradient_top"] - params["gradient_bottom"]
)
mountain_layer = mountain_layer.astype(np.uint8)

# Blend the mountain layer with the gradient background.
blended = cv2.addWeighted(gradient, params["blend_weight_gradient"],
                          mountain_layer, params["blend_weight_mountain"], 0)

# Apply a final light blur to ensure a very smooth, fluid appearance
final_blurred = cv2.GaussianBlur(blended,
                                 (params["gaussian_blur_final_kernel"], params["gaussian_blur_final_kernel"]),
                                 0)

# Convert to BGR for compatibility with common displays
final_img = cv2.cvtColor(final_blurred, cv2.COLOR_GRAY2BGR)

# Save and display the final background image
cv2.imwrite("btd6_mountain_background_customizable.png", final_img)
cv2.imshow("BTD6 Mountain Background", final_img)
cv2.waitKey(0)
cv2.destroyAllWindows()
