import React, { ReactNode, forwardRef, Ref } from 'react';
import Image from 'next/image';
import styles from './Button.module.css';
import Link from 'next/link';

interface ButtonProps {
  children?: ReactNode;
  buttonType: 'standard' | 'submit' | 'pending';
  width?: number;
  maxWidth?: number;
  styleType?: 'standard' | 'topBar' | 'danger';
  [key: string]: any;
}

/**
 * For rendering things that look like buttons, including actual buttons.
 */
const Button = forwardRef<HTMLDivElement, ButtonProps>((props, ref) => {

  const { children, buttonType, width, maxWidth, styleType, ...rest } = props;

  const attributes: {[key: string]: any} = {};

  // Default class and optional class for buttons in the top bar
  attributes.className = styles.button;
  if (styleType === 'topBar') {
    attributes.className += ' ' + styles.topBar;
  } else if (styleType === 'danger') {
    attributes.className += ' ' + styles.danger;
  }

  if (width) {
    // Fixed width
    attributes.style = {width: width};
  } else {
    // Variable width
    attributes.className += ' ' + styles.variableWidth;
    if (maxWidth) {
      attributes.style = {maxWidth: maxWidth};
    }
  }

  if (buttonType == 'pending') {
    // Render a pending button. This is non-functional and contains a throbber instead of text
    attributes.className += ' ' + styles.pending;
    return (
      <div ref={ref as Ref<HTMLDivElement> | undefined} {...attributes} {...rest}>
        <Image src={require('../images/throbber.gif')} alt="loading" width={20} height={20} />
      </div>
    )

  } else if (buttonType == 'submit') {
    // Render a form input submit
    return <button ref={ref as Ref<HTMLButtonElement> | undefined} {...attributes} {...rest}>{children}</button>
    
  }
  else {
    if (rest.href) {
      // Render a link that looks like a button
      return <Link href={rest.href} {...attributes} {...rest}>{children}</Link>

    } else {
      // Render a real button
      return <button ref={ref as Ref<HTMLButtonElement> | undefined} {...attributes} {...rest}>{children}</button>
    }
  }
});

Button.displayName = 'Button';
export default Button;
