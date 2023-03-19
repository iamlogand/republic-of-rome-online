import { useRef, useState } from 'react';
import Senator from '../../objects/Senator';

interface SenatorNameProps {
  senator: Senator;
  setInspectorRef: Function;
}

const SenatorName = (props: SenatorNameProps) => {

  const nameRef = useRef<HTMLDivElement>(null);

  const [inspectorTimer, setInspectorTimer] = useState<any>(null);

  const mouseEnter = () => {
    clearTimeout(inspectorTimer);
    setInspectorTimer(setTimeout(() => {
      const selfPosition = nameRef.current?.getBoundingClientRect();
      if (selfPosition) {
        props.setInspectorRef({
          XOffset: Math.round(selfPosition.x - 4),
          YOffset: Math.round(selfPosition.y),
          width: Math.round(selfPosition.width + 8),
          senator: props.senator,
          showPortrait: true
        });
      };
    }, 500));
  }

  const mouseLeave = () => {
    clearTimeout(inspectorTimer);
    setInspectorTimer(null);
    props.setInspectorRef(null);
  }

  return (
    <span ref={nameRef}>
      <a href="#" className='capitalize link' onMouseEnter={mouseEnter} onMouseLeave={mouseLeave}>
        {props.senator.getShortName()}
      </a>
    </span>
  )
}

export default SenatorName;
