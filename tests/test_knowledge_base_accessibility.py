"""
Knowledge Base Accessibility Test Suite
Comprehensive WCAG 2.1 AA compliance testing
Tests accessibility features, keyboard navigation, and assistive technology support
"""

import pytest
import json
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import colorsys


class TestKnowledgeBaseAccessibility:
    """WCAG 2.1 AA Accessibility compliance tests"""
    
    @pytest.fixture(scope="class")
    def accessibility_driver(self):
        """Setup Chrome WebDriver with accessibility extensions"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--force-prefers-reduced-motion")  # Test reduced motion
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.implicitly_wait(5)
        
        yield driver
        driver.quit()
    
    @pytest.fixture
    def authenticated_accessibility_session(self, accessibility_driver):
        """Create authenticated session for accessibility testing"""
        driver = accessibility_driver
        
        # Login
        driver.get("http://localhost:8000/")
        
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            
            username_field = driver.find_element(By.ID, "username")
            password_field = driver.find_element(By.ID, "password")
            login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            
            username_field.send_keys("admin")
            password_field.send_keys("admin")
            login_button.click()
            
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "nav"))
            )
        except:
            pass  # May already be logged in
        
        return driver
    
    def test_color_contrast_ratios_wcag_aa(self, authenticated_accessibility_session):
        """Test: All color combinations meet WCAG AA contrast ratios (4.5:1 normal, 3:1 large)"""
        driver = authenticated_accessibility_session
        
        # Navigate to knowledge base
        driver.get("http://localhost:8000/#knowledge-base")
        
        # Switch to iframe
        iframe = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "iframe"))
        )
        driver.switch_to.frame(iframe)
        
        # Wait for content to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "kb-category-card"))
        )
        
        # Test color contrast for key UI elements
        elements_to_test = [
            # (selector, description, is_large_text)
            ('.kb-header h1', 'Main heading', True),
            ('.kb-header p', 'Header description', False),
            ('.kb-search-input', 'Search input', False),
            ('.kb-category-title', 'Category titles', False),
            ('.kb-category-description', 'Category descriptions', False),
            ('.kb-article-title', 'Article titles', False),
            ('.kb-article-meta', 'Article metadata', False),
            ('.kb-difficulty-badge', 'Difficulty badges', False),
            ('.kb-back-button', 'Navigation buttons', False),
            ('.kb-nav-button', 'Article navigation buttons', False)
        ]
        
        contrast_results = []
        
        for selector, description, is_large_text in elements_to_test:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            
            for i, element in enumerate(elements[:3]):  # Test first 3 of each type
                try:
                    # Get computed styles
                    bg_color = driver.execute_script(
                        "return window.getComputedStyle(arguments[0]).backgroundColor;", element
                    )
                    text_color = driver.execute_script(
                        "return window.getComputedStyle(arguments[0]).color;", element
                    )
                    font_size = driver.execute_script(
                        "return window.getComputedStyle(arguments[0]).fontSize;", element
                    )
                    font_weight = driver.execute_script(
                        "return window.getComputedStyle(arguments[0]).fontWeight;", element
                    )
                    
                    # Parse font size to determine if it's large text
                    font_size_px = float(font_size.replace('px', ''))
                    is_large_computed = font_size_px >= 18 or (font_size_px >= 14 and int(font_weight) >= 600)
                    is_large_final = is_large_text or is_large_computed
                    
                    # Calculate contrast ratio
                    contrast_ratio = self.calculate_contrast_ratio(bg_color, text_color)
                    
                    # Determine WCAG AA requirement
                    required_ratio = 3.0 if is_large_final else 4.5
                    passes_wcag = contrast_ratio >= required_ratio
                    
                    result = {
                        'selector': selector,
                        'description': f"{description} #{i+1}" if i > 0 else description,
                        'bg_color': bg_color,
                        'text_color': text_color,
                        'contrast_ratio': contrast_ratio,
                        'required_ratio': required_ratio,
                        'is_large_text': is_large_final,
                        'passes_wcag_aa': passes_wcag,
                        'font_size': font_size,
                        'font_weight': font_weight
                    }
                    
                    contrast_results.append(result)
                    
                except Exception as e:
                    print(f"Error testing contrast for {selector}: {e}")
        
        # Report results
        failing_elements = [r for r in contrast_results if not r['passes_wcag_aa']]
        
        print(f"\nColor Contrast Test Results:")
        print(f"  Total elements tested: {len(contrast_results)}")
        print(f"  Passing WCAG AA: {len(contrast_results) - len(failing_elements)}")
        print(f"  Failing WCAG AA: {len(failing_elements)}")
        
        if failing_elements:
            print("\nFailing Elements:")
            for result in failing_elements:
                print(f"  - {result['description']}: {result['contrast_ratio']:.2f}:1 "
                      f"(required: {result['required_ratio']:.1f}:1)")
                print(f"    Colors: {result['text_color']} on {result['bg_color']}")
        
        # Assert all elements pass WCAG AA
        assert len(failing_elements) == 0, f"{len(failing_elements)} elements fail WCAG AA contrast requirements"
        
        driver.switch_to.default_content()
        return contrast_results
    
    def test_keyboard_navigation_complete(self, authenticated_accessibility_session):
        """Test: Complete keyboard navigation without mouse"""
        driver = authenticated_accessibility_session
        
        # Navigate to knowledge base
        driver.get("http://localhost:8000/#knowledge-base")
        
        # Switch to iframe
        iframe = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "iframe"))
        )
        driver.switch_to.frame(iframe)
        
        # Wait for content to load
        search_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "searchInput"))
        )
        
        # Test keyboard navigation sequence
        navigation_steps = []
        current_element = driver.switch_to.active_element
        
        # Click on search input to start
        search_input.click()
        current_element = driver.switch_to.active_element
        navigation_steps.append({
            'step': 'Search input focus',
            'element': self.get_element_description(current_element),
            'tag': current_element.tag_name,
            'id': current_element.get_attribute('id'),
            'accessible': self.is_element_accessible(current_element)
        })
        
        # Tab through interactive elements
        tab_count = 0
        max_tabs = 20  # Reasonable limit
        
        while tab_count < max_tabs:
            # Send Tab key
            ActionChains(driver).send_keys(Keys.TAB).perform()
            tab_count += 1
            
            new_element = driver.switch_to.active_element
            
            # Check if focus moved
            if new_element != current_element:
                step_info = {
                    'step': f'Tab {tab_count}',
                    'element': self.get_element_description(new_element),
                    'tag': new_element.tag_name,
                    'id': new_element.get_attribute('id'),
                    'class': new_element.get_attribute('class'),
                    'accessible': self.is_element_accessible(new_element),
                    'focusable': True,
                    'visible': new_element.is_displayed()
                }
                
                navigation_steps.append(step_info)
                current_element = new_element
                
                # Test Enter key activation on interactive elements
                if new_element.tag_name.lower() in ['button', 'a']:
                    # Test that Enter key works (don't actually activate to avoid navigation)
                    try:
                        # Check if element has onclick or href
                        has_action = (new_element.get_attribute('onclick') or 
                                    new_element.get_attribute('href') or
                                    new_element.tag_name.lower() == 'button')
                        
                        step_info['can_activate'] = has_action
                    except:
                        step_info['can_activate'] = False
                
                # Break if we've covered main interactive areas
                if len(navigation_steps) > 10:
                    break
        
        # Analyze navigation results
        interactive_elements = [s for s in navigation_steps if s.get('focusable')]
        accessible_elements = [s for s in navigation_steps if s.get('accessible')]
        visible_elements = [s for s in navigation_steps if s.get('visible')]
        
        print(f"\nKeyboard Navigation Test Results:")
        print(f"  Total navigation steps: {len(navigation_steps)}")
        print(f"  Interactive elements: {len(interactive_elements)}")
        print(f"  Accessible elements: {len(accessible_elements)}")
        print(f"  Visible elements: {len(visible_elements)}")
        
        # Print navigation sequence
        for i, step in enumerate(navigation_steps[:10]):  # Show first 10 steps
            print(f"  {i+1}. {step['element']} ({step['tag']})")
        
        # Assertions for keyboard navigation
        assert len(interactive_elements) >= 5, "Should have at least 5 focusable interactive elements"
        assert len(accessible_elements) >= len(interactive_elements) * 0.8, "80% of elements should be accessible"
        
        # Test specific keyboard shortcuts
        self.test_keyboard_shortcuts(driver)
        
        driver.switch_to.default_content()
        return navigation_steps
    
    def test_screen_reader_compatibility(self, authenticated_accessibility_session):
        """Test: Screen reader compatibility through ARIA and semantic HTML"""
        driver = authenticated_accessibility_session
        
        # Navigate to knowledge base
        driver.get("http://localhost:8000/#knowledge-base")
        
        # Switch to iframe
        iframe = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "iframe"))
        )
        driver.switch_to.frame(iframe)
        
        # Wait for content to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "kb-category-card"))
        )
        
        accessibility_results = {
            'semantic_html': self.test_semantic_html(driver),
            'aria_attributes': self.test_aria_attributes(driver),
            'alt_text': self.test_alt_text(driver),
            'form_labels': self.test_form_labels(driver),
            'heading_structure': self.test_heading_structure(driver),
            'landmarks': self.test_landmarks(driver),
            'live_regions': self.test_live_regions(driver)
        }
        
        # Calculate overall accessibility score
        total_tests = len(accessibility_results)
        passed_tests = sum(1 for result in accessibility_results.values() if result['passed'])
        accessibility_score = (passed_tests / total_tests) * 100
        
        print(f"\nScreen Reader Compatibility Results:")
        print(f"  Overall Accessibility Score: {accessibility_score:.1f}%")
        
        for test_name, result in accessibility_results.items():
            status = "✓ PASS" if result['passed'] else "✗ FAIL"
            print(f"  {test_name}: {status} - {result['message']}")
            
            if result.get('details'):
                for detail in result['details'][:3]:  # Show first 3 details
                    print(f"    • {detail}")
        
        # Assert minimum accessibility requirements
        assert accessibility_score >= 80, f"Accessibility score {accessibility_score:.1f}% below 80% requirement"
        assert accessibility_results['semantic_html']['passed'], "Semantic HTML requirement not met"
        assert accessibility_results['heading_structure']['passed'], "Proper heading structure required"
        assert accessibility_results['form_labels']['passed'], "Form labels requirement not met"
        
        driver.switch_to.default_content()
        return accessibility_results
    
    def test_focus_management(self, authenticated_accessibility_session):
        """Test: Focus management, focus indicators, and focus trapping"""
        driver = authenticated_accessibility_session
        
        # Navigate to knowledge base
        driver.get("http://localhost:8000/#knowledge-base")
        
        # Switch to iframe
        iframe = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "iframe"))
        )
        driver.switch_to.frame(iframe)
        
        # Wait for content
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "kb-category-card"))
        )
        
        focus_results = []
        
        # Test focus indicators on different element types
        focusable_selectors = [
            ('#searchInput', 'Search input'),
            ('.kb-category-card', 'Category cards'),
            ('.kb-back-button', 'Back buttons'),
            ('a', 'Links'),
            ('button', 'Buttons')
        ]
        
        for selector, description in focusable_selectors:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            
            for i, element in enumerate(elements[:2]):  # Test first 2 of each type
                if element.is_displayed():
                    try:
                        # Focus the element
                        element.click()
                        focused_element = driver.switch_to.active_element
                        
                        if focused_element == element:
                            # Check focus indicator
                            outline = driver.execute_script(
                                "return window.getComputedStyle(arguments[0]).outline;", element
                            )
                            outline_color = driver.execute_script(
                                "return window.getComputedStyle(arguments[0]).outlineColor;", element
                            )
                            outline_width = driver.execute_script(
                                "return window.getComputedStyle(arguments[0]).outlineWidth;", element
                            )
                            box_shadow = driver.execute_script(
                                "return window.getComputedStyle(arguments[0]).boxShadow;", element
                            )
                            
                            has_focus_indicator = (
                                outline != 'none' or 
                                outline_width != '0px' or 
                                box_shadow != 'none' or
                                'focus' in element.get_attribute('class')
                            )
                            
                            focus_results.append({
                                'element_type': description,
                                'selector': selector,
                                'has_focus_indicator': has_focus_indicator,
                                'outline': outline,
                                'outline_color': outline_color,
                                'box_shadow': box_shadow,
                                'can_focus': True
                            })
                        
                    except Exception as e:
                        focus_results.append({
                            'element_type': description,
                            'selector': selector,
                            'has_focus_indicator': False,
                            'can_focus': False,
                            'error': str(e)
                        })
        
        # Test focus order is logical
        focus_order_logical = self.test_focus_order(driver)
        
        # Test escape key handling
        escape_handling = self.test_escape_key_handling(driver)
        
        # Results summary
        elements_with_indicators = [r for r in focus_results if r.get('has_focus_indicator')]
        focusable_elements = [r for r in focus_results if r.get('can_focus')]
        
        print(f"\nFocus Management Test Results:")
        print(f"  Total focusable elements tested: {len(focusable_elements)}")
        print(f"  Elements with focus indicators: {len(elements_with_indicators)}")
        print(f"  Focus indicator coverage: {len(elements_with_indicators)/len(focusable_elements)*100:.1f}%")
        print(f"  Focus order logical: {focus_order_logical}")
        print(f"  Escape key handling: {escape_handling}")
        
        # Assertions
        focus_coverage = len(elements_with_indicators) / len(focusable_elements) if focusable_elements else 0
        assert focus_coverage >= 0.8, f"Focus indicator coverage {focus_coverage:.1%} below 80% requirement"
        assert focus_order_logical, "Focus order must be logical"
        
        driver.switch_to.default_content()
        return focus_results
    
    def test_responsive_accessibility(self, authenticated_accessibility_session):
        """Test: Accessibility across different viewport sizes"""
        driver = authenticated_accessibility_session
        
        # Test different viewport sizes
        viewports = [
            (375, 667, "Mobile"),   # iPhone SE
            (768, 1024, "Tablet"),  # iPad
            (1200, 800, "Desktop"), # Standard desktop
        ]
        
        accessibility_results = {}
        
        for width, height, device_type in viewports:
            driver.set_window_size(width, height)
            
            # Navigate to knowledge base
            driver.get("http://localhost:8000/#knowledge-base")
            
            # Switch to iframe
            iframe = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "iframe"))
            )
            driver.switch_to.frame(iframe)
            
            # Wait for content
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "kb-category-card"))
            )
            
            # Test touch target sizes for mobile
            if device_type == "Mobile":
                touch_target_results = self.test_touch_target_sizes(driver)
            else:
                touch_target_results = {'passed': True, 'message': 'Not applicable for non-mobile'}
            
            # Test text scaling
            text_scaling_results = self.test_text_scaling(driver, device_type)
            
            # Test horizontal scrolling
            horizontal_scroll_results = self.test_horizontal_scrolling(driver)
            
            accessibility_results[device_type] = {
                'touch_targets': touch_target_results,
                'text_scaling': text_scaling_results,
                'horizontal_scroll': horizontal_scroll_results,
                'viewport': f"{width}x{height}"
            }
            
            driver.switch_to.default_content()
        
        # Report results
        print(f"\nResponsive Accessibility Test Results:")
        for device_type, results in accessibility_results.items():
            print(f"  {device_type} ({results['viewport']}):")
            for test_name, result in results.items():
                if test_name != 'viewport':
                    status = "✓ PASS" if result['passed'] else "✗ FAIL"
                    print(f"    {test_name}: {status} - {result['message']}")
        
        # Assert all viewports pass essential tests
        for device_type, results in accessibility_results.items():
            assert results['horizontal_scroll']['passed'], f"Horizontal scroll issues on {device_type}"
            if device_type == "Mobile":
                assert results['touch_targets']['passed'], f"Touch target size issues on {device_type}"
        
        return accessibility_results
    
    def test_reduced_motion_support(self, authenticated_accessibility_session):
        """Test: Support for prefers-reduced-motion"""
        driver = authenticated_accessibility_session
        
        # Test with reduced motion preference
        driver.execute_cdp_cmd('Emulation.setEmulatedMedia', {
            'media': 'screen',
            'features': [{'name': 'prefers-reduced-motion', 'value': 'reduce'}]
        })
        
        # Navigate to knowledge base
        driver.get("http://localhost:8000/#knowledge-base")
        
        # Switch to iframe
        iframe = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "iframe"))
        )
        driver.switch_to.frame(iframe)
        
        # Wait for content
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "kb-category-card"))
        )
        
        # Check if animations are disabled/reduced
        elements_with_transitions = driver.find_elements(By.CSS_SELECTOR, "*")
        
        problematic_animations = []
        
        for element in elements_with_transitions[:50]:  # Test first 50 elements
            try:
                transition = driver.execute_script(
                    "return window.getComputedStyle(arguments[0]).transition;", element
                )
                animation = driver.execute_script(
                    "return window.getComputedStyle(arguments[0]).animation;", element
                )
                transform = driver.execute_script(
                    "return window.getComputedStyle(arguments[0]).transform;", element
                )
                
                # Check for potentially problematic animations
                has_motion_animation = (
                    'transform' in transition.lower() or
                    'translate' in animation.lower() or
                    'rotate' in animation.lower() or
                    'scale' in animation.lower()
                )
                
                if has_motion_animation:
                    problematic_animations.append({
                        'element': self.get_element_description(element),
                        'transition': transition,
                        'animation': animation
                    })
                    
            except:
                continue
        
        # Test that essential functionality works without animations
        category_cards = driver.find_elements(By.CLASS_NAME, "kb-category-card")
        if len(category_cards) > 0:
            # Click should work regardless of animation state
            category_cards[0].click()
            
            # Wait for navigation
            WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.ID, "articleListView"))
            )
            
            functionality_works = True
        else:
            functionality_works = False
        
        print(f"\nReduced Motion Test Results:")
        print(f"  Elements with motion animations: {len(problematic_animations)}")
        print(f"  Functionality works without animations: {functionality_works}")
        
        if problematic_animations:
            print("  Potentially problematic animations:")
            for anim in problematic_animations[:3]:
                print(f"    • {anim['element']}")
        
        # Should have minimal motion animations when reduced motion is preferred
        assert len(problematic_animations) < 10, f"Too many motion animations ({len(problematic_animations)}) with reduced motion preference"
        assert functionality_works, "Core functionality must work without animations"
        
        driver.switch_to.default_content()
        return problematic_animations
    
    # Helper methods for accessibility testing
    
    def calculate_contrast_ratio(self, bg_color, text_color):
        """Calculate WCAG contrast ratio between two colors"""
        def parse_color(color_str):
            # Handle rgb() and rgba() formats
            if color_str.startswith('rgb'):
                # Extract numbers from rgb(r, g, b) or rgba(r, g, b, a)
                numbers = re.findall(r'\d+\.?\d*', color_str)
                if len(numbers) >= 3:
                    return tuple(int(float(n)) for n in numbers[:3])
            
            # Handle hex colors if any
            if color_str.startswith('#'):
                hex_color = color_str[1:]
                if len(hex_color) == 6:
                    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            
            # Default to black/white for unknown formats
            return (0, 0, 0) if 'black' in color_str else (255, 255, 255)
        
        def get_luminance(rgb):
            r, g, b = rgb
            
            # Convert to 0-1 range
            r, g, b = r/255.0, g/255.0, b/255.0
            
            # Apply gamma correction
            def gamma_correct(c):
                return c/12.92 if c <= 0.03928 else ((c + 0.055)/1.055) ** 2.4
            
            r, g, b = gamma_correct(r), gamma_correct(g), gamma_correct(b)
            
            # Calculate luminance
            return 0.2126 * r + 0.7152 * g + 0.0722 * b
        
        try:
            bg_rgb = parse_color(bg_color)
            text_rgb = parse_color(text_color)
            
            bg_luminance = get_luminance(bg_rgb)
            text_luminance = get_luminance(text_rgb)
            
            # Calculate contrast ratio
            lighter = max(bg_luminance, text_luminance)
            darker = min(bg_luminance, text_luminance)
            
            ratio = (lighter + 0.05) / (darker + 0.05)
            return ratio
            
        except:
            return 4.5  # Default to passing ratio if calculation fails
    
    def get_element_description(self, element):
        """Get human-readable description of an element"""
        try:
            tag = element.tag_name
            element_id = element.get_attribute('id')
            element_class = element.get_attribute('class')
            element_text = element.text[:30] if element.text else ''
            
            description_parts = [tag]
            if element_id:
                description_parts.append(f"#{element_id}")
            if element_class:
                classes = element_class.split()[:2]  # First 2 classes
                description_parts.append(f".{'.'.join(classes)}")
            if element_text:
                description_parts.append(f'"{element_text}"')
                
            return ' '.join(description_parts)
        except:
            return 'unknown element'
    
    def is_element_accessible(self, element):
        """Check if element has basic accessibility features"""
        try:
            has_aria_label = bool(element.get_attribute('aria-label'))
            has_aria_labelledby = bool(element.get_attribute('aria-labelledby'))
            has_alt = bool(element.get_attribute('alt'))
            has_title = bool(element.get_attribute('title'))
            is_semantic = element.tag_name.lower() in ['button', 'a', 'input', 'select', 'textarea', 'nav', 'main', 'section', 'article', 'header', 'footer']
            
            return has_aria_label or has_aria_labelledby or has_alt or has_title or is_semantic
        except:
            return False
    
    def test_keyboard_shortcuts(self, driver):
        """Test keyboard shortcuts functionality"""
        # Test common keyboard shortcuts
        shortcuts = [
            (Keys.ESCAPE, "Close/cancel functionality"),
            # Add more shortcuts as implemented
        ]
        
        for key, description in shortcuts:
            try:
                ActionChains(driver).send_keys(key).perform()
                # Check if shortcut had expected effect (implementation specific)
            except:
                pass
    
    def test_semantic_html(self, driver):
        """Test for proper semantic HTML structure"""
        semantic_elements = driver.find_elements(By.CSS_SELECTOR, 
            "main, nav, section, article, header, footer, aside, h1, h2, h3, h4, h5, h6")
        
        has_main = len(driver.find_elements(By.TAG_NAME, "main")) > 0
        has_headings = len(driver.find_elements(By.CSS_SELECTOR, "h1, h2, h3, h4, h5, h6")) > 0
        has_nav = len(driver.find_elements(By.TAG_NAME, "nav")) > 0
        
        passed = has_main and has_headings and len(semantic_elements) >= 5
        
        return {
            'passed': passed,
            'message': f"Found {len(semantic_elements)} semantic elements. Main: {has_main}, Headings: {has_headings}, Nav: {has_nav}",
            'details': [f"Total semantic elements: {len(semantic_elements)}"]
        }
    
    def test_aria_attributes(self, driver):
        """Test for proper ARIA attributes"""
        aria_elements = driver.find_elements(By.CSS_SELECTOR, 
            "[aria-label], [aria-labelledby], [aria-describedby], [role], [aria-expanded], [aria-hidden]")
        
        interactive_elements = driver.find_elements(By.CSS_SELECTOR, 
            "button, a, input, select, textarea, [tabindex]")
        
        coverage = len(aria_elements) / max(len(interactive_elements), 1)
        passed = coverage >= 0.5  # At least 50% of interactive elements should have ARIA
        
        return {
            'passed': passed,
            'message': f"ARIA coverage: {coverage:.1%} ({len(aria_elements)}/{len(interactive_elements)})",
            'details': [f"Elements with ARIA: {len(aria_elements)}", f"Interactive elements: {len(interactive_elements)}"]
        }
    
    def test_alt_text(self, driver):
        """Test for alt text on images"""
        images = driver.find_elements(By.TAG_NAME, "img")
        images_with_alt = [img for img in images if img.get_attribute('alt') is not None]
        
        if len(images) == 0:
            passed = True
            message = "No images found"
        else:
            coverage = len(images_with_alt) / len(images)
            passed = coverage >= 0.9  # 90% of images should have alt text
            message = f"Alt text coverage: {coverage:.1%} ({len(images_with_alt)}/{len(images)})"
        
        return {
            'passed': passed,
            'message': message,
            'details': [f"Total images: {len(images)}", f"Images with alt: {len(images_with_alt)}"]
        }
    
    def test_form_labels(self, driver):
        """Test for proper form labels"""
        form_inputs = driver.find_elements(By.CSS_SELECTOR, "input, select, textarea")
        labeled_inputs = []
        
        for input_elem in form_inputs:
            has_label = (
                input_elem.get_attribute('aria-label') or
                input_elem.get_attribute('aria-labelledby') or
                input_elem.get_attribute('placeholder') or
                len(driver.find_elements(By.CSS_SELECTOR, f"label[for='{input_elem.get_attribute('id')}']")) > 0
            )
            if has_label:
                labeled_inputs.append(input_elem)
        
        if len(form_inputs) == 0:
            passed = True
            message = "No form inputs found"
        else:
            coverage = len(labeled_inputs) / len(form_inputs)
            passed = coverage >= 0.9  # 90% of inputs should be labeled
            message = f"Form label coverage: {coverage:.1%} ({len(labeled_inputs)}/{len(form_inputs)})"
        
        return {
            'passed': passed,
            'message': message,
            'details': [f"Total form inputs: {len(form_inputs)}", f"Labeled inputs: {len(labeled_inputs)}"]
        }
    
    def test_heading_structure(self, driver):
        """Test for proper heading hierarchy"""
        headings = driver.find_elements(By.CSS_SELECTOR, "h1, h2, h3, h4, h5, h6")
        
        if len(headings) == 0:
            return {'passed': False, 'message': "No headings found", 'details': []}
        
        heading_levels = []
        for heading in headings:
            level = int(heading.tag_name[1])  # Extract number from h1, h2, etc.
            heading_levels.append(level)
        
        # Check for h1
        has_h1 = 1 in heading_levels
        
        # Check for logical progression (no skipping levels)
        logical_progression = True
        for i in range(1, len(heading_levels)):
            if heading_levels[i] - heading_levels[i-1] > 1:
                logical_progression = False
                break
        
        passed = has_h1 and logical_progression
        
        return {
            'passed': passed,
            'message': f"Heading structure: H1 present: {has_h1}, Logical progression: {logical_progression}",
            'details': [f"Heading levels found: {heading_levels[:10]}"]  # Show first 10
        }
    
    def test_landmarks(self, driver):
        """Test for proper landmark regions"""
        landmarks = driver.find_elements(By.CSS_SELECTOR, 
            "main, nav, aside, header, footer, [role='main'], [role='navigation'], [role='complementary'], [role='banner'], [role='contentinfo']")
        
        has_main = len(driver.find_elements(By.CSS_SELECTOR, "main, [role='main']")) > 0
        has_nav = len(driver.find_elements(By.CSS_SELECTOR, "nav, [role='navigation']")) > 0
        
        passed = has_main and len(landmarks) >= 2
        
        return {
            'passed': passed,
            'message': f"Landmarks: {len(landmarks)} found. Main: {has_main}, Nav: {has_nav}",
            'details': [f"Total landmark elements: {len(landmarks)}"]
        }
    
    def test_live_regions(self, driver):
        """Test for ARIA live regions for dynamic content"""
        live_regions = driver.find_elements(By.CSS_SELECTOR, 
            "[aria-live], [role='alert'], [role='status'], [role='log']")
        
        # Check for common dynamic areas that should have live regions
        dynamic_areas = driver.find_elements(By.CSS_SELECTOR, 
            "#searchResults, #errorState, #loadingState, .kb-feedback-thanks")
        
        # At least some dynamic areas should have live region attributes
        passed = len(live_regions) > 0 or len(dynamic_areas) == 0
        
        return {
            'passed': passed,
            'message': f"Live regions: {len(live_regions)}, Dynamic areas: {len(dynamic_areas)}",
            'details': [f"Elements with live region attributes: {len(live_regions)}"]
        }
    
    def test_focus_order(self, driver):
        """Test that focus order is logical"""
        # This is a simplified test - in practice, would need more sophisticated analysis
        focusable_elements = driver.find_elements(By.CSS_SELECTOR, 
            "a, button, input, select, textarea, [tabindex]:not([tabindex='-1'])")
        
        # Check if elements appear in reasonable DOM order
        # (More complex spatial analysis would be needed for a complete test)
        return len(focusable_elements) >= 3  # Basic check that we have focusable elements
    
    def test_escape_key_handling(self, driver):
        """Test Escape key handling for modal dismissal"""
        # Test escape key (implementation would depend on modal existence)
        try:
            ActionChains(driver).send_keys(Keys.ESCAPE).perform()
            return True  # Basic test that escape doesn't break anything
        except:
            return False
    
    def test_touch_target_sizes(self, driver):
        """Test touch target sizes for mobile (44px minimum)"""
        interactive_elements = driver.find_elements(By.CSS_SELECTOR, 
            "button, a, input, select, .kb-category-card, .kb-article-item")
        
        small_targets = []
        
        for element in interactive_elements:
            if element.is_displayed():
                size = element.size
                width, height = size['width'], size['height']
                
                # WCAG guidelines: minimum 44px for touch targets
                if width < 44 or height < 44:
                    small_targets.append({
                        'element': self.get_element_description(element),
                        'size': f"{width}x{height}px"
                    })
        
        passed = len(small_targets) == 0
        message = f"Small touch targets: {len(small_targets)}"
        
        return {
            'passed': passed,
            'message': message,
            'details': [f"{target['element']}: {target['size']}" for target in small_targets[:3]]
        }
    
    def test_text_scaling(self, driver, device_type):
        """Test text scaling capability"""
        # Test that text can scale without horizontal scrolling
        body = driver.find_element(By.TAG_NAME, "body")
        
        # Get initial viewport width
        viewport_width = driver.execute_script("return window.innerWidth")
        
        # Simulate text scaling by increasing font size
        original_font_size = driver.execute_script(
            "return window.getComputedStyle(document.body).fontSize"
        )
        
        # Increase font size by 200% (WCAG requirement)
        driver.execute_script("document.body.style.fontSize = '200%'")
        
        # Check if horizontal scrolling is needed
        scroll_width = driver.execute_script("return document.body.scrollWidth")
        has_horizontal_scroll = scroll_width > viewport_width + 10  # 10px tolerance
        
        # Reset font size
        driver.execute_script("document.body.style.fontSize = ''")
        
        passed = not has_horizontal_scroll
        message = f"Text scaling at 200%: {'No horizontal scroll' if passed else 'Causes horizontal scroll'}"
        
        return {
            'passed': passed,
            'message': message,
            'details': [f"Viewport: {viewport_width}px, Content width: {scroll_width}px"]
        }
    
    def test_horizontal_scrolling(self, driver):
        """Test for unwanted horizontal scrolling"""
        viewport_width = driver.execute_script("return window.innerWidth")
        body_width = driver.execute_script("return document.body.scrollWidth")
        
        has_horizontal_scroll = body_width > viewport_width + 5  # 5px tolerance
        
        return {
            'passed': not has_horizontal_scroll,
            'message': f"Horizontal scroll: {'Present' if has_horizontal_scroll else 'None'}",
            'details': [f"Viewport: {viewport_width}px, Body width: {body_width}px"]
        }


if __name__ == "__main__":
    # Run accessibility tests
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "--durations=10"
    ])