# Universal
# com.google.fonts/check/family/win_ascent_and_descent

# Googlefonts


# com.google.fonts/check/STAT/gf_axisregistry # Can be fixed by rewriting the stat table
# com.google.fonts/check/colorfont_tables # Use maximum_color
# com.google.fonts/check/empty_glyph_on_gid1_for_colrv0 # Fix in gftools
# com.google.fonts/check/font_copyright # Rewrite metadata.pb copyright and name table (and gen OFL)
# com.google.fonts/check/description/urls # Remove http:// and https:// from anchor text
# com.google.fonts/check/description/eof_linebreak # Add crlf to end of to DESCRIPTION
# com.google.fonts/check/family/tnum_horizontal_metrics # Alter hmtx table
# com.google.fonts/check/ligature_carets # Add ligcarets to GDEF table
# com.google.fonts/check/glyf_nested_components # Decompose with a TTGlyph pen
# com.google.fonts/check/family/control_chars # Remove cmap entries for 0x01-0x1F
# com.google.fonts/check/gasp # fix-nonhinting
# com.google.fonts/check/old_ttfautohint # Strip hinting and reapply
# com.google.fonts/check/smart_dropout # gftools-fix-nonhinting
# com.google.fonts/check/vttclean # drop VTT tables
# com.google.fonts/check/integer_ppem_if_hinted# Fix in gftools?
# com.google.fonts/check/family/has_license # Create an OFL
# com.google.fonts/check/license/OFL_copyright # Create an OFL
# com.google.fonts/check/license/OFL_body_text # Crete an OFL
# com.google.fonts/check/name/license # Set LICENSE DESCRIPTION in name table and LICENSE_INFO_URL
# com.google.fonts/check/metadata/license # Set license to OFL in metadata.pb
# com.google.fonts/check/metadata/date_added # Fix metadata date
# com.google.fonts/check/metadata/menu_and_latin # Add menu and latin to subsets
# com.google.fonts/check/metadata/subsets_order # Reorder subsets
# com.google.fonts/check/metadata/copyright # Set copyright in each fonts{}
# com.google.fonts/check/metadata/familyname # Set family name in each fonts {}
# com.google.fonts/check/metadata/nameid/post_script_name # Put PS name from font into metadata
# com.google.fonts/check/metadata/match_fullname_postscript # Same
# com.google.fonts/check/metadata/valid_nameid25 # Fix nameID25 to end with Italic
# com.google.fonts/check/metadata/nameid/family_and_full_names # Sync font names with metadata names
# com.google.fonts/check/metadata/match_name_familyname # Set family per font {} to global name
# com.google.fonts/check/metadata/primary_script # Set primary script in metadata
# com.google.fonts/check/metadata/consistent_axis_enumeration # Crawl fvar table and use packager logic
# com_google_fonts_check_metadata_minisite_url # Remove trailing clutter
# com.google.fonts/check/name/unwanted_chars # ASCIIfy name tables
# com.google.fonts/check/name/version_format # Replace version with head version
# com.google.fonts/check/name/line_breaks # Remove line breaks from bame entries
# com.google.fonts/check/os2/use_typo_metrics # Set typo bit / gftools-fix
# com.google.fonts/check/fstype # Set to zero
# com.google.fonts/check/metadata/unsupported_subsets # Remove dead subsets
# com.google.fonts/check/aat # Drop apple tables
# com.google.fonts/check/no_debugging_tables # Drop debug tables
# com.google.fonts/check/STAT # Rebuild STAT table
# com.google.fonts/check/fvar_instances # Rebuild fvar instances (gftools)
# com.google.fonts/check/fvar_name_entries # Reubild instances
# com.google.fonts/check/varfont/has_HVAR # Generate from phantom points?
# com.google.fonts/check/varfont_duplicate_instance_names # Rebuild fvar?
# com.google.fonts/check/varfont/instances_in_order # Reorder fvar instances
# com.google.fonts/check/vertical_metrics # Set linegap etc.
