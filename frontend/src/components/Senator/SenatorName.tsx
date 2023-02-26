import Senator from '../../objects/Senator';

interface SenatorNameProps {
    senator: Senator;
  }

const SenatorName = (props: SenatorNameProps) => {

  return (
    <span>
      <a href="#" className='capitalize link'>{props.senator.name}</a>
    </span>
  )
}

export default SenatorName;
