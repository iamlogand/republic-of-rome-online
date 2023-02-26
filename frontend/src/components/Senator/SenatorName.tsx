import Senator from '../../objects/Senator';

interface SenatorNameProps {
    senator: Senator;
  }

const SenatorName = (props: SenatorNameProps) => {
  return <a className='capitalize link' href="ddddd">{props.senator.name}</a>
}

export default SenatorName;
