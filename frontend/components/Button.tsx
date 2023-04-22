import React, { MouseEventHandler, ReactNode, forwardRef, Ref, LegacyRef } from 'react';
import Image from 'next/image';
import styles from './Button.module.css';
import Link from 'next/link';

interface ButtonProps {
  text?: string;
  children?: ReactNode;
  onClick?: MouseEventHandler<HTMLElement>;
  href?: string;
  formSubmit?: boolean;
  pending?: boolean;
  width?: number;
  maxWidth?: number;
  styleType?: 'topBar';
}

/**
 * For rendering things that look like buttons, including actual buttons.
 * 
 * Set `formSubmit` to true if you need a form submission input element (overrides the default button or link).
 * Set `pending` to true for the text to be replaced with a non-functional pending button (overrides `formSubmit`).
 * 
 * The `text` and `children` props are mutually exclusive and required.
 * The `onClick` and `href` props are mutually exclusive and optional.
 * The `width` and `maxWidth` props are mutually exclusive and optional.
 */
const Button = forwardRef<HTMLDivElement, ButtonProps>((props, ref) => {
  const attributes: {[key: string]: any} = {};

  // Default class and optional class for buttons in the top bar
  attributes.className = styles.button;
  if (props.styleType === 'topBar') {
    attributes.className += ' ' + styles.topBar;
  }

  if (props.width) {
    // Fixed width
    attributes.style = {width: props.width};
  } else {
    // Variable width
    attributes.className += ' ' + styles.variableWidth;
    if (props.maxWidth) {
      attributes.style = {maxWidth: props.maxWidth};
    }
  }

  if (props.pending) {
    // Render a pending button. This is non-functional and contains a throbber instead of text
    return (
      <div ref={ref as Ref<HTMLDivElement> | undefined} {...attributes}>
        <Image src={require('../images/throbber.gif')} alt="loading" width={20} height={20} />
      </div>
    )

  } else if (props.formSubmit) {
    // Render a form input submit
    return (
      <button ref={ref as Ref<HTMLButtonElement> | undefined} {...attributes} type="submit">
        {props.text ? props.text : props.children}
      </button>
    )

  } else if (props.href) {
    // Render a link that looks like a button
    return (
      <Link href={props.href} {...attributes}>
        {props.text ? props.text : props.children}
      </Link>
    )
    
  } else {
    // Render a real button
    return (
      <button ref={ref as Ref<HTMLButtonElement> | undefined} onClick={props.onClick} type="button" {...attributes}>
        {props.text ? props.text : props.children}
      </button>
    )
  }
});

Button.displayName = 'Button';
export default Button;
