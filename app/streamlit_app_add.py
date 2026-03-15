"""
AI Analysis section for Page 2 of the Streamlit app — Project Okavango.

This code goes inside the block:
    elif page == "Page 2 - Image Viewer":
after the colleague's code (after st.write("Zoom:", zoom))

Add these imports at the top of streamlit_app.py, with the other imports:
    import yaml
    from pathlib import Path
    from ai_analysis import describe_image, assess_environmental_risk
"""

    # ─────────────────────────────────────────────────────────
    # BUTTON TO RUN THE AI ANALYSIS
    # ─────────────────────────────────────────────────────────

    if st.button("Analyse Area with AI"):

        # Path to the image downloaded by the other colleague
        image_path = f"images/satellite_{latitude}_{longitude}_{zoom}.png"

        # Check if the image exists on disk
        if not Path(image_path).exists():
            st.error("No image found for these coordinates. Please download the image first.")
        else:

            # Load settings from the models.yaml file
            with open("models.yaml", "r") as f:
                config = yaml.safe_load(f)

            image_model  = config["image_model"]["name"]
            image_prompt = config["image_model"]["prompt"]
            text_model   = config["text_model"]["name"]
            text_prompt  = config["text_model"]["prompt"]

            # ─────────────────────────────────────────────────
            # STEP 1: Show image and generate description
            # ─────────────────────────────────────────────────

            st.subheader("Satellite Image and AI Description")

            col1, col2 = st.columns(2)  # split the screen into 2 columns

            with col1:
                st.image(image_path, caption="Satellite Image", use_column_width=True)

            with col2:
                with st.spinner("Analysing image... (this may take 1-2 minutes)"):
                    description = describe_image(image_path, image_model, image_prompt)
                st.markdown("**AI Image Description:**")
                st.write(description)

            # ─────────────────────────────────────────────────
            # STEP 2: Assess environmental risk
            # ─────────────────────────────────────────────────

            st.subheader("Environmental Risk Assessment")

            with st.spinner("Assessing environmental risk..."):
                result = assess_environmental_risk(description, text_model, text_prompt)

            # Display the full model response
            st.markdown("**Risk Analysis:**")
            st.write(result["response"])

            # ─────────────────────────────────────────────────
            # VISUAL RISK INDICATOR
            # ─────────────────────────────────────────────────

            if result["is_at_risk"]:
                st.error("ENVIRONMENTAL RISK DETECTED — This area may be at risk.")
            else:
                st.success("NO SIGNIFICANT RISK DETECTED — This area appears safe.")
