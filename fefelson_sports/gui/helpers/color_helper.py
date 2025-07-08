import matplotlib.colors as mcolors

def hex_to_rgb(hex_color):
    """Convert a hex color string (e.g., '#FF0000') to an RGB tuple (e.g., (255, 0, 0))."""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 3:
        hex_color = ''.join(c * 2 for c in hex_color)  # Expand shorthand hex (e.g., #FFF to #FFFFFF)
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def color_difference(color1, color2):
    """Calculate the color difference between two RGB colors (normalized to 0-1 range)."""
    # Ensure both colors are normalized to 0-1 range for accurate comparison
    color1_normalized = tuple(c / 255.0 for c in color1)
    color2_normalized = tuple(c / 255.0 for c in color2)
    return sum((c1 - c2) ** 2 for c1, c2 in zip(color1_normalized, color2_normalized))

def closest_named_color(color_input):
    """
    Find the closest Matplotlib named color to a given hex color or RGB tuple.

    Args:
        color_input (str or tuple): Either a hex color string (e.g., '#FF0000') or an RGB tuple (e.g., (255, 0, 0)).

    Returns:
        str: The name of the closest Matplotlib named color, or 'grey' if an error occurs.
    """
    try:
        # Convert input to RGB tuple (0-255 range)
        if isinstance(color_input, str):
            target_rgb = hex_to_rgb(color_input)
        elif isinstance(color_input, tuple) and len(color_input) in (3, 4):
            # Ensure the RGB tuple values are in 0-255 range
            target_rgb = tuple(int(c) for c in color_input[:3])
            if any(c < 0 or c > 255 for c in target_rgb):
                raise ValueError("RGB values must be between 0 and 255")
        else:
            raise ValueError("Input must be a hex color string or an RGB tuple")

        # Find the closest named color
        closest_color = min(mcolors.cnames, key=lambda name: color_difference(target_rgb, hex_to_rgb(mcolors.cnames[name])))
        
        # Avoid returning 'white' as the closest color; use 'grey' instead
        closest_color = "grey" if closest_color == "white" else closest_color
        return closest_color

    except (ValueError, KeyError, TypeError) as e:
        # Log the error for debugging (optional)
        print(f"Error finding closest named color: {e}")
        return "grey"
    


class ColorScheme:
    # Theme 1: Neon Rainbow Rides (Bright, electric rainbow shades)
    neon_red = (255, 0, 0)          # Pure red
    neon_green = (0, 255, 0)         # Pure green

    # Theme 1: Cosmic Carnival
    # A dazzling interstellar fairground filled with swirling galaxies, glowing rides, and cosmic wonders.
    starburst_pink = (255, 105, 180)  # Hot pink glow of a supernova cotton candy cloud
    galaxy_swirl = (75, 0, 130)       # Deep indigo of a spiraling cosmic vortex
    meteor_mango = (255, 165, 0)      # Bright orange streak of a fruity meteor shower
    nebula_lime = (50, 205, 50)       # Zesty green haze of a glowing gas cloud
    comet_cyan = (0, 255, 255)        # Electric turquoise tail of a speeding comet
    ringmaster_red = (220, 20, 60)    # Bold crimson of a cosmic carnival tent
    stardust_gold = (255, 215, 0)     # Shimmering yellow of glittering space dust
    lunar_lavender = (147, 112, 219)  # Soft purple glow of a moonlit carousel
    orbit_olive = (128, 128, 0)       # Muted green of a planetary ring
    rocket_rust = (205, 92, 92)       # Warm reddish-brown of a retro space ride

    # Theme 2: Tropical Mirage
    # An exotic, dreamlike paradise where shimmering sands meet vibrant jungles and surreal waters.
    parrot_plum = (148, 0, 211)       # Rich violet of a tropical bird’s hidden feathers
    lagoon_teal = (0, 128, 128)       # Cool teal shimmer of an oasis pool
    coconut_cream = (245, 245, 220)   # Pale beige of sun-bleached island sands
    mango_mist = (255, 140, 0)        # Warm orange haze of a fruit-scented breeze
    coral_crush = (255, 127, 80)      # Vibrant peach of a reef at sunset
    palm_emerald = (0, 100, 0)        # Deep green of swaying jungle fronds
    pineapple_pop = (255, 250, 205)   # Light yellow zing of a tropical treat
    sahara_sapphire = (24, 116, 205)  # Bright blue mirage over desert dunes
    hibiscus_hot = (255, 0, 102)      # Fiery magenta of a blooming island flower
    tide_tangerine = (255, 99, 71)    # Tangy orange of a wave-kissed shore

    # Theme 3: Cyberpunk Neon
    # A gritty, futuristic cityscape pulsing with electric lights and high-tech chaos.
    glitch_glow = (0, 255, 127)       # Spring green flicker of a hacked hologram
    synth_violet = (138, 43, 226)     # Electric purple hum of a neon skyline
    data_dusk = (70, 130, 180)        # Steely blue of a digital twilight
    circuit_copper = (184, 115, 51)   # Metallic brown of glowing wires
    holo_haze = (173, 216, 230)       # Pale cyan shimmer of a virtual screen
    byte_blaze = (255, 69, 0)         # Red-orange flare of overclocked tech
    shadow_slate = (112, 128, 144)    # Cool gray of a rain-soaked alley
    laser_lemon = (255, 255, 102)     # Sharp yellow beam cutting through fog
    grid_grape = (186, 85, 211)       # Punchy purple of a pulsing network
    chrome_chill = (192, 192, 192)    # Sleek silver of a polished cyber surface

    # Theme 4: Mystic Forest
    # An enchanted woodland shrouded in mist, alive with magical hues and ethereal light.
    fairy_fog = (240, 248, 255)       # Ghostly white mist hiding ancient secrets
    moss_mint = (60, 179, 113)        # Fresh green of a spellbound carpet
    twilight_taupe = (139, 69, 19)    # Earthy brown of dusk-kissed bark
    sprite_sky = (135, 206, 235)      # Soft blue of a magical canopy breach
    lichen_lilac = (218, 112, 214)    # Delicate purple of glowing fungi
    ember_elm = (178, 34, 34)         # Deep red flicker of a hidden flame
    willow_wisp = (144, 238, 144)     # Pale green shimmer of wandering spirits
    rune_rose = (188, 143, 143)       # Dusty pink of carved mystic symbols
    shadow_sage = (85, 107, 47)       # Muted green of a cloaked grove
    moon_mauve = (199, 21, 133)       # Rich mauve of a lunar-lit clearing
    dark_matter_haunted_house = (47, 79, 79) 
    black = (0,0,0)


    @staticmethod
    def to_matplotlib_color(rgb_tuple):
        """Convert an RGB tuple to a Matplotlib-compatible color."""
        # First, try to find the closest named color
        return closest_named_color(rgb_tuple)
    

def brightness(color):
    # Calculate brightness using the formula: 0.299 * R + 0.587 * G + 0.114 * B
    return 0.299 * color[0] + 0.587 * color[1] + 0.114 * color[2]

def adjust_color_for_readability(color, brightness_adjustment, saturation_adjustment, hue_adjustment):
    adjusted_color = (
        max(0, min(255, color[0] + brightness_adjustment)),
        max(0, min(255, color[1] + saturation_adjustment)),
        max(0, min(255, color[2] + hue_adjustment))
    )
    return adjusted_color

def calculate_contrast_ratio(color1, color2):

    luminance1 = calculate_relative_luminance(color1)
    luminance2 = calculate_relative_luminance(color2)

    contrast_ratio = (max(luminance1, luminance2) + 0.05) / (min(luminance1, luminance2) + 0.05)
    return contrast_ratio

def adjust_gamma(color_component):
    color = color_component / 255.0
    if color <= 0.04045:
        return color / 12.92
    else:
        return ((color + 0.055) / 1.055) ** 2.4

def calculate_relative_luminance(color):
    r, g, b = color
    return 0.2126 * adjust_gamma(r) + 0.7152 * adjust_gamma(g) + 0.0722 * adjust_gamma(b)


def adjust_readability(background_color, text_color, target_contrast=5, max_iterations=10):

    current_contrast = calculate_contrast_ratio(text_color, background_color)
    iterations = 0

    while current_contrast < target_contrast and iterations < max_iterations:
        # Determine which color is darker and adjust its brightness, saturation, and hue
        if brightness(background_color) > brightness(text_color):
            text_color = adjust_color_for_readability(text_color, -10, -5, 0)
            background_color = adjust_color_for_readability(background_color, 10, 5, 0)
        else:
            text_color = adjust_color_for_readability(text_color, +10, 5, 0)
            background_color = adjust_color_for_readability(background_color, -10, -5, 0)

        # Recalculate the contrast ratio
        current_contrast = calculate_contrast_ratio(text_color, background_color)
        iterations += 1

    return background_color, text_color
        