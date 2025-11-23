"""
EvidenceCheck MVP - Streamlit Application

Main entry point for the EvidenceCheck video-text consistency checker.
Provides a simple UI for uploading videos and analyzing text descriptions.
"""

import streamlit as st
from video_analyzer import analyze_video
from text_parser import extract_claims
from scoring import score_consistency
import tempfile
import cv2
import os


def main():
    """Main Streamlit application entry point."""
    st.set_page_config(
        page_title="EvidenceCheck MVP",
        page_icon="🔍",
        layout="wide"
    )
    
    st.title("🔍 EvidenceCheck MVP")
    st.markdown("**Video ↔ Text Consistency Checker**")
    st.markdown("""
    Upload a short video (10-30 seconds) and a text description to check consistency.
    
    **Supported Claims:**
    - Number of people
    - Number of cars/vehicles
    - Presence or absence of weapons
    """)
    
    st.divider()
    
    # File uploader for video
    video_file = st.file_uploader(
        "Upload a short video (10-30 seconds)",
        type=["mp4", "mov", "avi", "mkv"],
        help="Supported formats: MP4, MOV, AVI, MKV"
    )
    
    # Text area for description
    text_desc = st.text_area(
        "Paste the incident description here",
        height=150,
        placeholder="Example: 'There were three people and two cars in the parking lot. No weapons were present.'",
        help="Describe what should be in the video (people count, cars count, weapon presence)"
    )
    
    st.divider()
    
    # Analyze button
    if st.button("🔍 Analyze", type="primary", use_container_width=True):
        if not video_file:
            st.error("❌ Please upload a video file.")
            return
        
        if not text_desc or not text_desc.strip():
            st.error("❌ Please provide a text description.")
            return
        
        # Save video to temporary file
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
                tmp.write(video_file.read())
                tmp_path = tmp.name
            
            # Analyze video
            with st.spinner("📹 Analyzing video... This may take a moment."):
                try:
                    video_stats = analyze_video(tmp_path)
                except Exception as e:
                    st.error(f"❌ Error analyzing video: {str(e)}")
                    os.unlink(tmp_path)
                    return
            
            # Extract claims from text
            with st.spinner("📝 Parsing text description..."):
                try:
                    claims = extract_claims(text_desc)
                except Exception as e:
                    st.error(f"❌ Error parsing text: {str(e)}")
                    os.unlink(tmp_path)
                    return
            
            # Score consistency
            with st.spinner("⚖️ Calculating consistency score..."):
                try:
                    result = score_consistency(claims, video_stats)
                except Exception as e:
                    st.error(f"❌ Error calculating score: {str(e)}")
                    os.unlink(tmp_path)
                    return
            
            # Clean up temporary file
            try:
                os.unlink(tmp_path)
            except:
                pass
            
            # Display results
            st.success("✅ Analysis complete!")
            st.divider()
            
            # Score display
            score = result['score']
            score_color = "🟢" if score >= 80 else "🟡" if score >= 50 else "🔴"
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.markdown(f"### {score_color} Consistency Score: **{score}/100**")
            
            st.divider()
            
            # Details table
            st.subheader("📊 Claim Analysis Details")
            
            if result["details"]:
                # Display details in a table format
                import pandas as pd
                
                details_df = pd.DataFrame(result["details"])
                
                # Format the display
                display_df = details_df.copy()
                display_df.columns = ["Claim Type", "Claim Value", "Video Value", "Result", "Note"]
                
                st.dataframe(
                    display_df,
                    use_container_width=True,
                    hide_index=True
                )
                
                # Show individual claim results
                for detail in result["details"]:
                    claim_type = detail["claim_type"].title()
                    claim_value = detail["claim_value"]
                    video_value = detail["video_value"]
                    result_status = detail["result"]
                    
                    status_emoji = "✅" if result_status == "supported" else "⚠️" if result_status == "partial" else "❌"
                    
                    st.markdown(f"""
                    **{status_emoji} {claim_type}**: Claimed `{claim_value}`, Detected `{video_value}` → *{result_status}*
                    - *{detail["note"]}*
                    """)
            else:
                st.info("ℹ️ No claims were extracted from the text description. Please include mentions of people, cars, or weapons.")
            
            st.divider()
            
            # Display video statistics
            st.subheader("📹 Video Analysis Summary")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("People Detected", video_stats.get("people", 0))
            with col2:
                st.metric("Cars Detected", video_stats.get("cars", 0))
            with col3:
                weapon_status = "Yes" if video_stats.get("weapon_present", False) else "No"
                st.metric("Weapon Detected", weapon_status)
            
            st.divider()
            
            # Display sample frames
            st.subheader("🎬 Sample Frames with Detections")
            
            frames = video_stats.get("frames", [])
            if frames:
                # Display frames in a grid
                cols = st.columns(min(len(frames), 3))
                for idx, frame in enumerate(frames[:3]):  # Limit to 3 frames
                    with cols[idx % len(cols)]:
                        # Convert BGR to RGB for display
                        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        st.image(frame_rgb, use_container_width=True, caption=f"Frame {idx + 1}")
            else:
                st.warning("⚠️ No frames available for display.")
            
            # Show extracted claims
            st.divider()
            with st.expander("🔍 Extracted Claims from Text"):
                st.json(claims)
            
            with st.expander("📹 Video Statistics"):
                video_stats_display = {k: v for k, v in video_stats.items() if k != "frames"}
                video_stats_display["frames_count"] = len(frames)
                st.json(video_stats_display)
        
        except Exception as e:
            st.error(f"❌ An unexpected error occurred: {str(e)}")
            st.exception(e)
            # Clean up temp file if it exists
            try:
                if 'tmp_path' in locals():
                    os.unlink(tmp_path)
            except:
                pass
    
    st.divider()
    st.markdown("""
    ### 📋 Usage Tips
    
    1. **Video Requirements:**
       - Length: 10-30 seconds
       - Format: MP4, MOV, AVI, or MKV
       - Daytime/well-lit scenes work best
       - Single camera, minimal motion
    
    2. **Text Description Examples:**
       - "There were three people and two cars in the parking lot."
       - "Two men and one woman were present. No weapons were visible."
       - "A single car was parked with no people around."
    
    3. **Supported Claims:**
       - People: Use numbers or words (e.g., "three people", "2 persons")
       - Cars: Use numbers or words (e.g., "two cars", "1 vehicle")
       - Weapons: Mention presence or absence (e.g., "gun present", "no weapon")
    """)


if __name__ == "__main__":
    main()

