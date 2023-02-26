import { useRef, useState } from 'react';
import Senator from '../../objects/Senator';

interface SenatorNameProps {
  senator: Senator;
  setSummaryRef: Function;
}

const SenatorName = (props: SenatorNameProps) => {

  const nameRef = useRef<HTMLDivElement>(null);

  const [summaryTimer, setSummaryTimer] = useState<any>(null);

  const mouseEnter = () => {
    clearTimeout(summaryTimer);
    setSummaryTimer(setTimeout(() => {
      const selfPosition = nameRef.current?.getBoundingClientRect();
      if (selfPosition) {
        props.setSummaryRef({
          XOffset: Math.round(selfPosition.x - 4),
          YOffset: Math.round(selfPosition.y),
          width: Math.round(selfPosition.width + 8),
          instance: props.senator,
          showPortrait: true
        });
      };
    }, 500));
  }

  const mouseLeave = () => {
    clearTimeout(summaryTimer);
    setSummaryTimer(null);
    props.setSummaryRef(null);
  }

  return (
    <span ref={nameRef}>
      <a href="#" className='capitalize link' onMouseEnter={mouseEnter} onMouseLeave={mouseLeave}>
        {props.senator.name}
      </a>
    </span>
  )
}

export default SenatorName;
