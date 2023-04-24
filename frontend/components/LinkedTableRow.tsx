import React from 'react';
import styles from "./LinkedTableRow.module.css";

interface LinkedTableRowProps {
  href: string;
  children: React.ReactNode[];
}

const LinkedTableRow = (props: LinkedTableRowProps) => {

  const handleKeyPress = (event: React.KeyboardEvent<HTMLTableRowElement>) => {
    
    if (event.key === 'Enter' || event.key === ' ') {
      window.location.href = props.href;
    }
  };

  return (
    <tr
      className={styles.row}
      onClick={() => (window.location.href = props.href)}
      onKeyDown={handleKeyPress}
      tabIndex={0}
    >
      {props.children.map((child, index) => (
        <td key={index}>{child}</td>
      ))}
    </tr>
  );
};

export default LinkedTableRow;
