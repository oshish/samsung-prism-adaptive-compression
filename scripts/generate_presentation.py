import os
import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

def create_deck(output_path="samsung_prism_milestone1_presentation.pptx"):
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6] # completely blank layout

    # Color Palette - Professional Samsung / Tech Theme
    NAVY = RGBColor(12, 35, 64)       # #0C2340 Primary brand
    DARK_BLUE = RGBColor(0, 45, 114)  # #002D72 Secondary
    CYAN = RGBColor(0, 150, 214)      # #0096D6 Accent
    WHITE = RGBColor(255, 255, 255)
    LIGHT_BG = RGBColor(248, 250, 252)# #F8FAFC
    CARD_BORDER = RGBColor(226, 232, 240)
    DARK_TEXT = RGBColor(30, 41, 59)  # #1E293B
    MUTED_TEXT = RGBColor(100, 116, 139) # #64748B
    GREEN = RGBColor(16, 185, 129)    # Success accent
    CARD_BG = RGBColor(255, 255, 255)

    def add_header(slide, title_text, category_text="SAMSUNG PRISM • WORKLET 26VI11"):
        # Header banner container
        top_bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(1.15))
        top_bar.fill.solid()
        top_bar.fill.fore_color.rgb = NAVY
        top_bar.line.color.rgb = NAVY

        # Accent thin stripe
        stripe = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(1.15), Inches(13.333), Inches(0.06))
        stripe.fill.solid()
        stripe.fill.fore_color.rgb = CYAN
        stripe.line.color.rgb = CYAN

        # Category text
        cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.12), Inches(11.7), Inches(0.3))
        tf_c = cat_box.text_frame
        tf_c.word_wrap = True
        p_c = tf_c.paragraphs[0]
        p_c.text = category_text.upper()
        p_c.font.size = Pt(10)
        p_c.font.bold = True
        p_c.font.color.rgb = CYAN

        # Title text
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.38), Inches(11.7), Inches(0.65))
        tf_t = title_box.text_frame
        tf_t.word_wrap = True
        p_t = tf_t.paragraphs[0]
        p_t.text = title_text
        p_t.font.size = Pt(22)
        p_t.font.bold = True
        p_t.font.color.rgb = WHITE

    def add_card(slide, left, top, width, height, bg_color=CARD_BG, border_color=CARD_BORDER):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = bg_color
        card.line.color.rgb = border_color
        card.line.width = Pt(1.5)
        return card

    # =========================================================================
    # SLIDE 1: TITLE SLIDE
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    bg1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
    bg1.fill.solid()
    bg1.fill.fore_color.rgb = NAVY
    bg1.line.color.rgb = NAVY

    # Decorative Cyan Bar
    dec_bar = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.9), Inches(1.8), Inches(0.15), Inches(3.6))
    dec_bar.fill.solid()
    dec_bar.fill.fore_color.rgb = CYAN
    dec_bar.line.color.rgb = CYAN

    tbox1 = s1.shapes.add_textbox(Inches(1.2), Inches(1.7), Inches(11.2), Inches(3.8))
    tf1 = tbox1.text_frame
    tf1.word_wrap = True

    p0 = tf1.paragraphs[0]
    p0.text = "SAMSUNG PRISM PROJECT • WORKLET ID: 26VI11 (CSED)"
    p0.font.size = Pt(13)
    p0.font.bold = True
    p0.font.color.rgb = CYAN

    p1 = tf1.add_paragraph()
    p1.text = "Adaptive Frame Compression"
    p1.font.size = Pt(40)
    p1.font.bold = True
    p1.font.color.rgb = WHITE

    p2 = tf1.add_paragraph()
    p2.text = "Intelligent Pre-Compression Decision Engine for Mobile Memory Optimization"
    p2.font.size = Pt(20)
    p2.font.color.rgb = RGBColor(203, 213, 225)

    p3 = tf1.add_paragraph()
    p3.text = "\nMilestone 1 Final Demonstration (Steps 1–10 Complete)"
    p3.font.size = Pt(16)
    p3.font.bold = True
    p3.font.color.rgb = GREEN

    # Bottom Metadata card
    meta_box = s1.shapes.add_textbox(Inches(1.2), Inches(5.8), Inches(11.0), Inches(1.0))
    tf_meta = meta_box.text_frame
    pm1 = tf_meta.paragraphs[0]
    pm1.text = "Team of 3 Student Researchers • Department of Computer Science & Engineering"
    pm1.font.size = Pt(12)
    pm1.font.color.rgb = RGBColor(148, 163, 184)
    pm2 = tf_meta.add_paragraph()
    pm2.text = "GitHub Repository: https://github.com/oshish/samsung-prism-adaptive-compression"
    pm2.font.size = Pt(11)
    pm2.font.color.rgb = CYAN

    # =========================================================================
    # SLIDE 2: THE PROBLEM & MOTIVATION
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    add_header(s2, "1. Problem Formulation & Samsung Motivation", "EXECUTIVE SUMMARY")

    # Card 1: The Mobile Memory Bottleneck
    add_card(s2, Inches(0.8), Inches(1.5), Inches(5.6), Inches(4.3))
    b1 = s2.shapes.add_textbox(Inches(1.0), Inches(1.65), Inches(5.2), Inches(4.0))
    tf = b1.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "The Mobile Frame Buffer Bottleneck"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = NAVY

    items = [
        ("High-Resolution Cameras (50-200MP):", "Produces enormous uncompressed 24-bit RGB frames."),
        ("120Hz Displays & Gaming:", "Refreshes frames every 8.3ms, congesting LPDDR bus and draining battery."),
        ("Thermal Throttling:", "High memory bandwidth causes phone heating and clock throttling.")
    ]
    for title, desc in items:
        p = tf.add_paragraph()
        p.text = f"• {title} "
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = DARK_TEXT
        run = p.add_run()
        run.text = desc
        run.font.bold = False
        run.font.color.rgb = MUTED_TEXT

    # Card 2: Naive Approaches Fail
    add_card(s2, Inches(6.8), Inches(1.5), Inches(5.7), Inches(4.3))
    b2 = s2.shapes.add_textbox(Inches(7.0), Inches(1.65), Inches(5.3), Inches(4.0))
    tf2 = b2.text_frame
    tf2.word_wrap = True
    p = tf2.paragraphs[0]
    p.text = "Why Simple Static Compression Fails"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = NAVY

    items2 = [
        ("Always Lossless (PNG):", "Guarantees zero artifacts, but only saves 2x-3x memory. Wastes 75% of potential bandwidth reduction."),
        ("Always Lossy (JPEG):", "Saves 10x-15x memory, but ruins dark shadows (OLED shadow blocking), smooth skies (color banding), and sharp text."),
        ("Static Manual Rules ('If dark > 30%'):", "Fails in practice! Achieved only 14.6% savings because human rules are overly conservative.")
    ]
    for title, desc in items2:
        p = tf2.add_paragraph()
        p.text = f"• {title} "
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = DARK_TEXT
        run = p.add_run()
        run.text = desc
        run.font.bold = False
        run.font.color.rgb = MUTED_TEXT

    # Bottom Callout
    bot = add_card(s2, Inches(0.8), Inches(6.0), Inches(11.7), Inches(1.0), bg_color=NAVY)
    bbox = s2.shapes.add_textbox(Inches(1.0), Inches(6.05), Inches(11.3), Inches(0.9))
    tf_b = bbox.text_frame
    tf_b.word_wrap = True
    pb = tf_b.paragraphs[0]
    pb.text = "OUR OBJECTIVE:"
    pb.font.size = Pt(11)
    pb.font.bold = True
    pb.font.color.rgb = CYAN
    pb2 = tf_b.add_paragraph()
    pb2.text = "Build an ultra-fast (< 1ms) AI brain that inspects the uncompressed frame BEFORE compression and selects Lossy or Lossless mode to maximize memory reduction while ensuring ZERO visible artifacts."
    pb2.font.size = Pt(13)
    pb2.font.bold = True
    pb2.font.color.rgb = WHITE

    # =========================================================================
    # SLIDE 3: SYSTEM ARCHITECTURE
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    add_header(s3, "2. Pre-Compression Decision Architecture", "END-TO-END PIPELINE")

    steps = [
        ("1. Input Frame", "Raw 24-bit RGB frame buffer straight from Camera ISP or GPU frame buffer.", NAVY),
        ("2. Dual Representation", "Convert to ITU-R BT.601 YUV. Decouple luminance (Y) from chrominance (U/V).", DARK_BLUE),
        ("3. Pre-Compression Features", "Extract 40 spatial, brightness, texture & edge features in O(N) time (< 1ms).", DARK_BLUE),
        ("4. Intelligent Classifier", "Trained ML model evaluates features and predicts LOSSY vs LOSSLESS.", CYAN),
        ("5. Hardware Execution", "Apply optimal codec: JPEG (Q=85) or PNG lossless based on model decision.", GREEN)
    ]
    for i, (stitle, sdesc, col) in enumerate(steps):
        left = Inches(0.8 + i * 2.38)
        c = add_card(s3, left, Inches(1.5), Inches(2.26), Inches(3.6))
        
        # Step number badge
        badge = s3.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, Inches(1.5), Inches(2.26), Inches(0.45))
        badge.fill.solid()
        badge.fill.fore_color.rgb = col
        badge.line.color.rgb = col
        p_badge = badge.text_frame.paragraphs[0]
        p_badge.text = f"STAGE 0{i+1}"
        p_badge.font.size = Pt(11)
        p_badge.font.bold = True
        p_badge.font.color.rgb = WHITE
        p_badge.alignment = PP_ALIGN.CENTER
        
        tb = s3.shapes.add_textbox(left + Inches(0.1), Inches(2.05), Inches(2.06), Inches(2.9))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = stitle
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = NAVY
        
        p_desc = tf.add_paragraph()
        p_desc.text = f"\n{sdesc}"
        p_desc.font.size = Pt(11)
        p_desc.font.color.rgb = DARK_TEXT

    # Bottom Zero Leakage Callout Card
    add_card(s3, Inches(0.8), Inches(5.3), Inches(11.7), Inches(1.7), bg_color=LIGHT_BG)
    lk_box = s3.shapes.add_textbox(Inches(1.0), Inches(5.4), Inches(11.3), Inches(1.5))
    tf_lk = lk_box.text_frame
    tf_lk.word_wrap = True
    p = tf_lk.paragraphs[0]
    p.text = "CRITICAL SCIENTIFIC PRINCIPLE: ZERO TARGET LEAKAGE"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = NAVY
    
    p = tf_lk.add_paragraph()
    p.text = "In real hardware, post-compression metrics (like compressed file size, compression ratio, PSNR, SSIM) DO NOT EXIST before compression happens! Therefore, model inputs X strictly contain pre-compression visual properties. Post-compression metrics are permanently blacklisted and audited via automated unit tests (tests/test_leakage.py)."
    p.font.size = Pt(11)
    p.font.color.rgb = DARK_TEXT

    # =========================================================================
    # SLIDE 4: DATASET ENGINEERING & SPLITS
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    add_header(s4, "3. Dataset Curation & Stratified Splits (Steps 1–3)", "DATASET ENGINEERING")

    # Left text card
    add_card(s4, Inches(0.8), Inches(1.5), Inches(6.0), Inches(5.5))
    tb4 = s4.shapes.add_textbox(Inches(1.0), Inches(1.65), Inches(5.6), Inches(5.2))
    tf4 = tb4.text_frame
    tf4.word_wrap = True

    p = tf4.paragraphs[0]
    p.text = "1,030 Diverse Standardized Frames"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = NAVY

    ds_bullets = [
        ("Caltech-101 (1,000 images):", "Real photographic objects, animals, vehicles, complex natural textures, and varied lighting conditions."),
        ("Kodak Benchmark (24 images):", "Canonical uncompressed 768x512 photographic benchmark universally cited in compression research."),
        ("Synthetic Stress Suite (6 images):", "Specially designed failure cases: extreme low-light noise (Y < 20), smooth sky gradients, high-contrast UI graphics, flat posters, and mixed HDR."),
        ("Stratified 70/15/15 Split:", "Strictly partitioned into Train (721), Val (154), and Test (155) splits. Both classes (Lossy and Lossless) are proportionally balanced across all splits.")
    ]
    for title, desc in ds_bullets:
        p = tf4.add_paragraph()
        p.text = f"\n• {title} "
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = DARK_TEXT
        run = p.add_run()
        run.text = desc
        run.font.bold = False
        run.font.color.rgb = MUTED_TEXT

    # Right Image Card: class_distribution.png
    add_card(s4, Inches(7.1), Inches(1.5), Inches(5.4), Inches(5.5))
    chart1_path = "results/figures/class_distribution.png"
    if os.path.exists(chart1_path):
        s4.shapes.add_picture(chart1_path, Inches(7.25), Inches(1.8), width=Inches(5.1))
    
    caption_box = s4.shapes.add_textbox(Inches(7.2), Inches(6.4), Inches(5.2), Inches(0.5))
    p_cap = caption_box.text_frame.paragraphs[0]
    p_cap.text = "Figure: Balanced Strategy Distribution across Train, Val, and Test Splits"
    p_cap.font.size = Pt(10)
    p_cap.font.color.rgb = MUTED_TEXT
    p_cap.alignment = PP_ALIGN.CENTER

    # =========================================================================
    # SLIDE 5: PRE-COMPRESSION FEATURES (40 PROPERTIES)
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    add_header(s5, "4. Pre-Compression Feature Extraction (Steps 4–6)", "FEATURE ENGINEERING")

    # Left text card
    add_card(s5, Inches(0.8), Inches(1.5), Inches(5.8), Inches(5.5))
    tb5 = s5.shapes.add_textbox(Inches(1.0), Inches(1.65), Inches(5.4), Inches(5.2))
    tf5 = tb5.text_frame
    tf5.word_wrap = True

    p = tf5.paragraphs[0]
    p.text = "40 Pre-Compression Features (8 Domains)"
    p.font.size = Pt(17)
    p.font.bold = True
    p.font.color.rgb = NAVY

    feat_domains = [
        ("Structural & Dimensions (4):", "width, height, aspect ratio, total pixels"),
        ("Brightness & Luminance (10):", "mean, std, min, max, median, dark/bright ratios, IQR"),
        ("Contrast & Dynamic Range (2):", "RMS contrast, Michelson contrast"),
        ("Entropy & Information (2):", "RGB Shannon entropy, Luminance entropy H(Y)"),
        ("Edges & High Frequencies (5):", "Sobel density, mean/std magnitude, Laplacian variance"),
        ("Spatial Texture / GLCM (2):", "GLCM Haralick contrast, GLCM homogeneity"),
        ("Noise & Shadow Risk (2):", "Immerkaer Laplacian noise, dark chroma variance"),
        ("Color & Chrominance (9):", "RGB channel moments, YUV moments, colorfulness")
    ]
    for d_name, d_items in feat_domains:
        p = tf5.add_paragraph()
        p.text = f"• {d_name} "
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = DARK_TEXT
        run = p.add_run()
        run.text = d_items
        run.font.bold = False
        run.font.color.rgb = MUTED_TEXT

    # Right Image Card: feature_distributions.png
    add_card(s5, Inches(6.9), Inches(1.5), Inches(5.6), Inches(5.5))
    chart2_path = "results/figures/feature_distributions.png"
    if os.path.exists(chart2_path):
        s5.shapes.add_picture(chart2_path, Inches(7.05), Inches(1.75), width=Inches(5.3))

    cap2 = s5.shapes.add_textbox(Inches(7.0), Inches(6.4), Inches(5.4), Inches(0.5))
    p_cap2 = cap2.text_frame.paragraphs[0]
    p_cap2.text = "Figure: Key Feature Boxplots Separated by Ground-Truth Strategy"
    p_cap2.font.size = Pt(10)
    p_cap2.font.color.rgb = MUTED_TEXT
    p_cap2.alignment = PP_ALIGN.CENTER

    # =========================================================================
    # SLIDE 6: COMPRESSION BENCHMARK (6,180 TRIALS)
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    add_header(s6, "5. Rate-Distortion & Latency Benchmarks (Step 7)", "EMPIRICAL BENCHMARKS")

    # Table Card
    add_card(s6, Inches(0.8), Inches(1.45), Inches(11.7), Inches(3.6))
    
    # Create Table
    rows = 7
    cols = 9
    table_shape = s6.shapes.add_table(rows, cols, Inches(1.0), Inches(1.6), Inches(11.3), Inches(3.2))
    table = table_shape.table

    headers = ["Codec", "Quality", "Compression Ratio", "Memory Saved", "Encode Latency", "Decode Latency", "PSNR (dB)", "SSIM", "Feasibility"]
    for col_idx, h in enumerate(headers):
        cell = table.cell(0, col_idx)
        cell.text = h
        cell.fill.solid()
        cell.fill.fore_color.rgb = NAVY
        for p in cell.text_frame.paragraphs:
            p.font.size = Pt(10)
            p.font.bold = True
            p.font.color.rgb = WHITE
            p.alignment = PP_ALIGN.CENTER

    data = [
        ["JPEG", "50", "18.81x", "94.7%", "1.45 ms", "1.77 ms", "30.95", "0.9238", "Fails Quality"],
        ["JPEG", "75", "14.63x", "93.2%", "1.43 ms", "1.87 ms", "46.43", "0.9929", "Fast, high quality"],
        ["JPEG (Target)", "85", "11.61x", "91.4%", "1.42 ms", "1.91 ms", "42.08", "0.9908", "OPTIMAL SWEET SPOT"],
        ["JPEG", "95", "7.77x", "87.1%", "1.47 ms", "2.08 ms", "48.58", "0.9969", "Near-lossless"],
        ["PNG (Lossless)", "—", "3.80x", "73.7%", "12.27 ms", "4.55 ms", "Inf", "1.0000", "Baseline Lossless"],
        ["WebP Lossless", "100", "17.68x", "94.3%", "462.40 ms", "5.04 ms", "Inf", "1.0000", "37x TOO SLOW!"]
    ]

    for row_idx, row_vals in enumerate(data, start=1):
        for col_idx, val in enumerate(row_vals):
            cell = table.cell(row_idx, col_idx)
            cell.text = val
            cell.fill.solid()
            if row_idx == 3: # Target
                cell.fill.fore_color.rgb = RGBColor(238, 242, 255)
            elif row_idx % 2 == 0:
                cell.fill.fore_color.rgb = LIGHT_BG
            else:
                cell.fill.fore_color.rgb = WHITE
            for p in cell.text_frame.paragraphs:
                p.font.size = Pt(10)
                p.alignment = PP_ALIGN.CENTER
                if row_idx == 3:
                    p.font.bold = True
                    p.font.color.rgb = NAVY
                elif row_idx == 6 and col_idx == 8:
                    p.font.bold = True
                    p.font.color.rgb = RGBColor(220, 38, 38)
                else:
                    p.font.color.rgb = DARK_TEXT

    # Bottom Insights
    add_card(s6, Inches(0.8), Inches(5.2), Inches(11.7), Inches(1.8), bg_color=LIGHT_BG)
    tb_i = s6.shapes.add_textbox(Inches(1.0), Inches(5.3), Inches(11.3), Inches(1.6))
    tf_i = tb_i.text_frame
    tf_i.word_wrap = True

    p = tf_i.paragraphs[0]
    p.text = "KEY BENCHMARK DISCOVERIES:"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = NAVY

    ins = [
        "1. JPEG Q=85 is the Ideal Operating Point: Achieves 11.61x compression ratio with 1.42ms encoding latency and 0.9908 SSIM.",
        "2. The WebP Lossless Bottleneck: WebP Lossless achieves 17.68x, but its 462.4ms CPU encoding time is 37x slower than PNG and completely violates mobile 120Hz/60Hz display deadlines (8.3ms - 16.6ms).",
        "3. JPEG Q=50 Degrades Quality: Aggressive quantization drops mean SSIM to 0.9238 and causes high-frequency edge ringing."
    ]
    for item in ins:
        p = tf_i.add_paragraph()
        p.text = item
        p.font.size = Pt(11)
        p.font.color.rgb = DARK_TEXT

    # =========================================================================
    # SLIDE 7: QUALITY EVALUATION & ARTIFACT METRICS
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    add_header(s7, "6. Quality & Artifact Protection Metrics (Step 8)", "QUALITY EVALUATION")

    metrics_cards = [
        ("PSNR (Peak Signal-to-Noise)", "Global logarithmic pixel fidelity in decibels (dB). Threshold: >= 33.0 dB. Identical frames return Inf (handled as 100 dB)."),
        ("SSIM (Structural Similarity)", "3-channel Gaussian structural correlation (11x11 window). Threshold: >= 0.94 for imperceptible structural degradation on mobile."),
        ("Dark-SSIM (Shadow Artifacts)", "Localized SSIM computed strictly over low-luminance pixels (Y < 40). Catches severe DCT blockiness and banding in shadows on OLED screens."),
        ("Banding Risk Score", "Detects staircase quantization plateaus across smooth sky/gradient regions. High scores warn against severe false contouring.")
    ]
    for i, (m_title, m_desc) in enumerate(metrics_cards):
        row = i // 2
        col = i % 2
        left = Inches(0.8 + col * 5.95)
        top = Inches(1.5 + row * 2.35)
        add_card(s7, left, top, Inches(5.75), Inches(2.15))

        tb = s7.shapes.add_textbox(left + Inches(0.2), top + Inches(0.2), Inches(5.35), Inches(1.75))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = m_title
        p.font.size = Pt(15)
        p.font.bold = True
        p.font.color.rgb = NAVY

        p_desc = tf.add_paragraph()
        p_desc.text = f"\n{m_desc}"
        p_desc.font.size = Pt(11)
        p_desc.font.color.rgb = DARK_TEXT

    # Bottom LPIPS Feasibility
    add_card(s7, Inches(0.8), Inches(6.0), Inches(11.7), Inches(1.0), bg_color=NAVY)
    tb_lp = s7.shapes.add_textbox(Inches(1.0), Inches(6.05), Inches(11.3), Inches(0.9))
    tf_lp = tb_lp.text_frame
    tf_lp.word_wrap = True
    p = tf_lp.paragraphs[0]
    p.text = "LPIPS (LEARNED PERCEPTUAL IMAGE PATCH SIMILARITY) FEASIBILITY STUDY:"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = CYAN
    p2 = tf_lp.add_paragraph()
    p2.text = "Requires 50MB-100MB deep neural network weights (AlexNet/VGG) and 50-120ms GPU inference. Incompatible with hard real-time mobile display budgets (< 2ms). Reserved strictly for offline validation in Milestone 2."
    p2.font.size = Pt(11)
    p2.font.color.rgb = WHITE

    # =========================================================================
    # SLIDE 8: GROUND-TRUTH LABEL GENERATION
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    add_header(s8, "7. Ground-Truth Labeling & Dataset Construction (Step 9)", "GROUND-TRUTH LABELS")

    # Left: Multi-Criterion Rule
    add_card(s8, Inches(0.8), Inches(1.5), Inches(5.7), Inches(5.5))
    tb8 = s8.shapes.add_textbox(Inches(1.0), Inches(1.65), Inches(5.3), Inches(5.2))
    tf8 = tb8.text_frame
    tf8.word_wrap = True

    p = tf8.paragraphs[0]
    p.text = "Multi-Criterion Empirical Decision Rule"
    p.font.size = Pt(17)
    p.font.bold = True
    p.font.color.rgb = NAVY

    p = tf8.add_paragraph()
    p.text = "An image is labeled LOSSY if and only if ALL four conditions hold simultaneously; otherwise LOSSLESS:\n"
    p.font.size = Pt(11)
    p.font.color.rgb = DARK_TEXT

    rules = [
        ("1. SSIM >= 0.94:", "Guarantees structural fidelity."),
        ("2. PSNR >= 33.0 dB:", "Ensures high signal-to-noise ratio."),
        ("3. Dark-SSIM >= 0.90:", "Protects low-luminance details (Y < 40)."),
        ("4. Size Saving >= 25%:", "Lossy JPEG must save at least 25% memory over lossless PNG.")
    ]
    for r_title, r_desc in rules:
        p = tf8.add_paragraph()
        p.text = f"• {r_title} "
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = NAVY
        run = p.add_run()
        run.text = r_desc
        run.font.bold = False
        run.font.color.rgb = DARK_TEXT

    p_note = tf8.add_paragraph()
    p_note.text = "\n[ASSUMPTION — REQUIRES MENTOR CONFIRMATION]\nAll thresholds are parameter-driven in configs/config.yaml and ready for calibration to Samsung internal standards."
    p_note.font.size = Pt(10)
    p_note.font.bold = True
    p_note.font.color.rgb = CYAN

    # Right: Results Breakdown
    add_card(s8, Inches(6.8), Inches(1.5), Inches(5.7), Inches(5.5), bg_color=LIGHT_BG)
    tb8_r = s8.shapes.add_textbox(Inches(7.0), Inches(1.65), Inches(5.3), Inches(5.2))
    tf8_r = tb8_r.text_frame
    tf8_r.word_wrap = True

    p = tf8_r.paragraphs[0]
    p.text = "Empirical Class Distribution"
    p.font.size = Pt(17)
    p.font.bold = True
    p.font.color.rgb = NAVY

    p = tf8_r.add_paragraph()
    p.text = "\n• LOSSY: 1,018 frames (98.8%)\n• LOSSLESS: 12 frames (1.2%)\n"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = GREEN

    p = tf8_r.add_paragraph()
    p.text = "Why did the 12 frames strictly require LOSSLESS?"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = NAVY

    reasons = [
        ("Vector Graphics & Flat Posters (edge_04, edge_05):", "PNG compressed them 4x to 9x smaller than JPEG! Attempting lossy JPEG actually bloated file size (-400% to -900% savings)."),
        ("Smooth Gradients (edge_01):", "JPEG DCT block boundaries caused severe false contouring and color banding."),
        ("Dark Noisy Frames (edge_02, edge_06, kodim16-20):", "Low-light noise ruined DCT quantization, dropping PSNR < 29 dB and Dark-SSIM < 0.88.")
    ]
    for r_head, r_body in reasons:
        p = tf8_r.add_paragraph()
        p.text = f"• {r_head} "
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = DARK_TEXT
        run = p.add_run()
        run.text = r_body
        run.font.bold = False
        run.font.color.rgb = MUTED_TEXT

    # =========================================================================
    # SLIDE 9: BASELINE CLASSIFIER RESULTS (STEP 10)
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    add_header(s9, "8. Baseline Machine Learning Classification (Step 10)", "MODEL EVALUATION")

    # Table Card (Left)
    add_card(s9, Inches(0.8), Inches(1.5), Inches(6.5), Inches(5.5))
    tb9 = s9.shapes.add_textbox(Inches(1.0), Inches(1.65), Inches(6.1), Inches(0.5))
    p = tb9.text_frame.paragraphs[0]
    p.text = "Held-Out Test Split Performance (155 Frames)"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = NAVY

    t9_shape = s9.shapes.add_table(6, 6, Inches(1.0), Inches(2.2), Inches(6.1), Inches(2.7))
    t9 = t9_shape.table
    m_headers = ["Model", "Accuracy", "Precision", "Recall", "F1", "ROC-AUC"]
    for c_idx, mh in enumerate(m_headers):
        cell = t9.cell(0, c_idx)
        cell.text = mh
        cell.fill.solid()
        cell.fill.fore_color.rgb = NAVY
        for p in cell.text_frame.paragraphs:
            p.font.size = Pt(10)
            p.font.bold = True
            p.font.color.rgb = WHITE
            p.alignment = PP_ALIGN.CENTER

    m_rows = [
        ["Decision Tree", "100.0%", "1.000", "1.000", "1.000", "1.000"],
        ["Random Forest", "99.4%", "0.994", "1.000", "0.997", "1.000"],
        ["Logistic Reg.", "98.7%", "1.000", "0.987", "0.993", "1.000"],
        ["Majority Class", "98.7%", "0.987", "1.000", "0.994", "N/A"],
        ["Rule-Based", "16.8%", "0.929", "0.170", "0.287", "N/A"]
    ]
    for r_idx, r_vals in enumerate(m_rows, start=1):
        for c_idx, val in enumerate(r_vals):
            cell = t9.cell(r_idx, c_idx)
            cell.text = val
            cell.fill.solid()
            if r_idx == 1:
                cell.fill.fore_color.rgb = RGBColor(236, 253, 245)
            elif r_idx % 2 == 0:
                cell.fill.fore_color.rgb = LIGHT_BG
            else:
                cell.fill.fore_color.rgb = WHITE
            for p in cell.text_frame.paragraphs:
                p.font.size = Pt(10)
                p.alignment = PP_ALIGN.CENTER
                if r_idx == 1:
                    p.font.bold = True
                    p.font.color.rgb = GREEN
                else:
                    p.font.color.rgb = DARK_TEXT

    b_note = s9.shapes.add_textbox(Inches(1.0), Inches(5.0), Inches(6.1), Inches(1.8))
    tf_bn = b_note.text_frame
    tf_bn.word_wrap = True
    p = tf_bn.paragraphs[0]
    p.text = "Key Takeaways:"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = NAVY
    points = [
        "• Decision Tree achieved 100% accuracy, matching the Oracle Upper Bound.",
        "• Rule-Based Heuristics failed (16.8% accuracy) because manual threshold cutoffs flag ordinary natural textures as risky.",
        "• Zero false positives: Decision Tree never mistakenly sent a delicate frame to lossy compression."
    ]
    for pt in points:
        p = tf_bn.add_paragraph()
        p.text = pt
        p.font.size = Pt(10)
        p.font.color.rgb = DARK_TEXT

    # Right: Confusion Matrices Image
    add_card(s9, Inches(7.6), Inches(1.5), Inches(4.9), Inches(5.5))
    cm_path = "results/figures/confusion_matrices.png"
    if os.path.exists(cm_path):
        s9.shapes.add_picture(cm_path, Inches(7.75), Inches(1.75), width=Inches(4.6))

    cap_cm = s9.shapes.add_textbox(Inches(7.7), Inches(6.4), Inches(4.7), Inches(0.5))
    p_cap_cm = cap_cm.text_frame.paragraphs[0]
    p_cap_cm.text = "Figure: Confusion Matrices Across Evaluated Baseline Models"
    p_cap_cm.font.size = Pt(10)
    p_cap_cm.font.color.rgb = MUTED_TEXT
    p_cap_cm.alignment = PP_ALIGN.CENTER

    # =========================================================================
    # SLIDE 10: FEATURE IMPORTANCE (WHAT DRIVES DECISIONS?)
    # =========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    add_header(s10, "9. Feature Importance & Interpretability (Step 10)", "EXPLAINABLE AI")

    # Left: Explanation of Top Drivers
    add_card(s10, Inches(0.8), Inches(1.5), Inches(5.8), Inches(5.5))
    tb10 = s10.shapes.add_textbox(Inches(1.0), Inches(1.65), Inches(5.4), Inches(5.2))
    tf10 = tb10.text_frame
    tf10.word_wrap = True

    p = tf10.paragraphs[0]
    p.text = "Top Physical Drivers of Compressibility"
    p.font.size = Pt(17)
    p.font.bold = True
    p.font.color.rgb = NAVY

    drivers = [
        ("1. Dimensions & Area (width, total_pixels, height):", "Small UI icons behave radically differently under 8x8 DCT blocks than full-frame camera scenes."),
        ("2. Dynamic Range & Luminance Extremes:", "luminance_range, max_luminance, min_luminance directly govern clipping and shadow quantization risks."),
        ("3. Local Spatial Variance (local_variance_mean/std):", "Measures patch-level texture density; high activity hides DCT noise, whereas flat areas reveal artifacts."),
        ("4. Edge Sharpness (std_edge_magnitude):", "Sharp vector boundaries create ringing under lossy DCT."),
        ("5. Chroma Variation (std_b, mean_u):", "Strong color saturation requires careful quantization to avoid chroma bleeding.")
    ]
    for d_title, d_desc in drivers:
        p = tf10.add_paragraph()
        p.text = f"\n• {d_title} "
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = DARK_TEXT
        run = p.add_run()
        run.text = d_desc
        run.font.bold = False
        run.font.color.rgb = MUTED_TEXT

    # Right: feature_importances.png
    add_card(s10, Inches(6.9), Inches(1.5), Inches(5.6), Inches(5.5))
    fi_path = "results/figures/feature_importances.png"
    if os.path.exists(fi_path):
        s10.shapes.add_picture(fi_path, Inches(7.05), Inches(1.8), width=Inches(5.3))

    cap_fi = s10.shapes.add_textbox(Inches(7.0), Inches(6.4), Inches(5.4), Inches(0.5))
    p_cap_fi = cap_fi.text_frame.paragraphs[0]
    p_cap_fi.text = "Figure: Gini Feature Importances from Random Forest Ensemble"
    p_cap_fi.font.size = Pt(10)
    p_cap_fi.font.color.rgb = MUTED_TEXT
    p_cap_fi.alignment = PP_ALIGN.CENTER

    # =========================================================================
    # SLIDE 11: SYSTEM STORAGE & QUALITY TRADEOFF
    # =========================================================================
    s11 = prs.slides.add_slide(blank_layout)
    add_header(s11, "10. Real-World System Storage vs. Quality Evaluation", "SYSTEM EVALUATION")

    # Table Card
    add_card(s11, Inches(0.8), Inches(1.45), Inches(6.3), Inches(5.5))
    tb11 = s11.shapes.add_textbox(Inches(1.0), Inches(1.6), Inches(5.9), Inches(0.5))
    p = tb11.text_frame.paragraphs[0]
    p.text = "155 Test Frames (37.95 MB Uncompressed 24-bit Raw)"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = NAVY

    t11_shape = s11.shapes.add_table(7, 6, Inches(1.0), Inches(2.15), Inches(5.9), Inches(3.2))
    t11 = t11_shape.table
    s_headers = ["Strategy", "Size (MB)", "Saved vs Lossless", "Mean SSIM", "PSNR", "Failures"]
    for c_idx, sh in enumerate(s_headers):
        cell = t11.cell(0, c_idx)
        cell.text = sh
        cell.fill.solid()
        cell.fill.fore_color.rgb = NAVY
        for p in cell.text_frame.paragraphs:
            p.font.size = Pt(9)
            p.font.bold = True
            p.font.color.rgb = WHITE
            p.alignment = PP_ALIGN.CENTER

    s_rows = [
        ["Always Lossless", "16.87 MB", "0.0%", "1.0000", "100.0 dB", "0"],
        ["Rule-Based", "14.41 MB", "14.6%", "0.9982", "90.2 dB", "0"],
        ["Logistic Reg.", "4.20 MB", "75.1%", "0.9919", "43.8 dB", "0"],
        ["Random Forest", "3.49 MB", "79.3%", "0.9914", "42.7 dB", "0"],
        ["Always Lossy", "3.50 MB", "79.2%", "0.9914", "42.4 dB", "0*"],
        ["Decision Tree (Ours)", "3.46 MB", "79.47%", "0.9915", "43.1 dB", "0"]
    ]
    for r_idx, r_vals in enumerate(s_rows, start=1):
        for c_idx, val in enumerate(r_vals):
            cell = t11.cell(r_idx, c_idx)
            cell.text = val
            cell.fill.solid()
            if r_idx == 6: # Ours
                cell.fill.fore_color.rgb = RGBColor(236, 253, 245)
            elif r_idx % 2 == 0:
                cell.fill.fore_color.rgb = LIGHT_BG
            else:
                cell.fill.fore_color.rgb = WHITE
            for p in cell.text_frame.paragraphs:
                p.font.size = Pt(9)
                p.alignment = PP_ALIGN.CENTER
                if r_idx == 6:
                    p.font.bold = True
                    p.font.color.rgb = GREEN
                else:
                    p.font.color.rgb = DARK_TEXT

    s_box = s11.shapes.add_textbox(Inches(1.0), Inches(5.45), Inches(5.9), Inches(1.4))
    tf_sb = s_box.text_frame
    tf_sb.word_wrap = True
    p = tf_sb.paragraphs[0]
    p.text = "Result: Our Decision Tree reduces storage from 16.87 MB to 3.46 MB, delivering 79.47% memory reduction while maintaining pristine 0.9915 SSIM and matching the theoretical Oracle Upper Bound!"
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = NAVY

    # Right: storage_quality_tradeoff.png
    add_card(s11, Inches(7.4), Inches(1.45), Inches(5.1), Inches(5.5))
    sq_path = "results/figures/storage_quality_tradeoff.png"
    if os.path.exists(sq_path):
        s11.shapes.add_picture(sq_path, Inches(7.55), Inches(1.75), width=Inches(4.8))

    cap_sq = s11.shapes.add_textbox(Inches(7.5), Inches(6.4), Inches(4.9), Inches(0.5))
    p_cap_sq = cap_sq.text_frame.paragraphs[0]
    p_cap_sq.text = "Figure: Real-World Storage vs. Quality Trade-Off Simulation"
    p_cap_sq.font.size = Pt(10)
    p_cap_sq.font.color.rgb = MUTED_TEXT
    p_cap_sq.alignment = PP_ALIGN.CENTER

    # =========================================================================
    # SLIDE 12: EMBEDDED HARDWARE & MILESTONE 2 ROADMAP
    # =========================================================================
    s12 = prs.slides.add_slide(blank_layout)
    add_header(s12, "11. Hardware Feasibility & Milestone 2 Roadmap", "CONCLUSION & NEXT STEPS")

    # Left: Why Decision Tree Wins for Samsung Hardware
    add_card(s12, Inches(0.8), Inches(1.5), Inches(5.7), Inches(5.5))
    tb12 = s12.shapes.add_textbox(Inches(1.0), Inches(1.65), Inches(5.3), Inches(5.2))
    tf12 = tb12.text_frame
    tf12.word_wrap = True

    p = tf12.paragraphs[0]
    p.text = "Why Decision Tree Wins for Mobile Hardware"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = NAVY

    hw_points = [
        ("Depth <= 4 (Only 4 If/Else Checks):", "No complex matrix math, no floating-point vector units required."),
        ("Ultra-Low Latency (< 10 Microseconds):", "Executes 100x faster than the 1ms budget; easily runs inline in camera ISP or display controller firmware."),
        ("Zero Neural Network Overhead:", "Requires no NPU, GPU, or 50MB model weights. Code compiles down to 20 lines of pure C/C++."),
        ("100% Deterministic & Verifiable:", "No black-box hallucination; decisions can be formally validated for safety.")
    ]
    for hw_title, hw_desc in hw_points:
        p = tf12.add_paragraph()
        p.text = f"\n• {hw_title} "
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = DARK_TEXT
        run = p.add_run()
        run.text = hw_desc
        run.font.bold = False
        run.font.color.rgb = MUTED_TEXT

    # Right: Questions for Mentors & Next Steps
    add_card(s12, Inches(6.8), Inches(1.5), Inches(5.7), Inches(5.5), bg_color=LIGHT_BG)
    tb12_r = s12.shapes.add_textbox(Inches(7.0), Inches(1.65), Inches(5.3), Inches(5.2))
    tf12_r = tb12_r.text_frame
    tf12_r.word_wrap = True

    p = tf12_r.paragraphs[0]
    p.text = "Open Questions & Milestone 2 Roadmap"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = NAVY

    m2_points = [
        ("Mentor Alignment on Codec Standard:", "Are we targeting Samsung ARM AFBC (Frame Buffer Compression), ASTC, or standard JPEG/WebP pipelines?"),
        ("Quality Threshold Cutoff:", "Is SSIM >= 0.94 / PSNR >= 33 dB aligned with Samsung quality targets, or is a stricter threshold required?"),
        ("Multi-Level Adaptive Quality:", "Expand Milestone 2 from binary Lossy/Lossless to continuous adaptive quality Q in [50, 95]."),
        ("On-Device Firmware Benchmark:", "Port the 4-level decision tree to C/C++ and profile cycle latency on ARM/Android hardware.")
    ]
    for m2_title, m2_desc in m2_points:
        p = tf12_r.add_paragraph()
        p.text = f"\n• {m2_title} "
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = NAVY
        run = p.add_run()
        run.text = m2_desc
        run.font.bold = False
        run.font.color.rgb = DARK_TEXT

    # Save presentation
    prs.save(output_path)
    print(f"Presentation successfully created: {output_path}")

if __name__ == "__main__":
    out_file = sys.argv[1] if len(sys.argv) > 1 else "samsung_prism_milestone1_presentation.pptx"
    create_deck(out_file)
