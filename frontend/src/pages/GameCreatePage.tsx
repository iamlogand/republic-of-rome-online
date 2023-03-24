import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import request from "../helpers/requestHelper";

interface GameCreatePageProps {
  accessToken: string,
  refreshToken: string,
  setAuthData: Function
}

const GameCreatePage = (props: GameCreatePageProps) => {
  const [name, setName] = useState<string>('');
  const [nameFeedback, setNameFeedback] = useState<string>('');
  const [description, setDescription] = useState<string>('');
  const [descriptionFeedback, setDescriptionFeedback] = useState<string>('');
  const navigate = useNavigate();
  
  const handleNameChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setName(event.target.value);
  }

  const handleDescriptionChange = (event: React.ChangeEvent<HTMLTextAreaElement>) => {
    setDescription(event.target.value);
  }

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    const gameData = {
      name: name,
      description: description
    }

    const response = await request('POST', 'games/', props.accessToken, props.refreshToken, props.setAuthData, gameData);
    if (response) {
      if (response.status === 201) {
        navigate('/game-list');
      } else {
        if (response.data) {
          if (response.data.name && Array.isArray(response.data.name) && response.data.name.length > 0) {
            setNameFeedback(response.data.name[0]);
          } else {
            setNameFeedback('');
          }
          if (response.data.description && Array.isArray(response.data.description) && response.data.description.length > 0) {
            setDescriptionFeedback(response.data.description[0]);
          } else {
            setDescriptionFeedback('');
          }
        }
      }
    }
  }

  return (
    <main id="standard_page" aria-label="Home Page">
      <section className='row'>
        <Link to=".." className="button" style={{width: "90px"}}>◀&nbsp; Back</Link>
        <h2>Create Game</h2>
      </section>
      <section>
        <form onSubmit={handleSubmit}>
          <label htmlFor="name" className={nameFeedback && 'error'}>Name</label>
          <input required
            id="name"
            className={`field ${nameFeedback && 'error'}`}
            onChange={handleNameChange} />
          {nameFeedback && <div className="field-feedback" role="alert">{nameFeedback}</div>}
          <label htmlFor="description" className={descriptionFeedback && 'error'}>Description</label>
          <textarea
            id="description"
            className={`field ${descriptionFeedback && 'error'}`}
            rows={3}
            onChange={handleDescriptionChange} style={{width: "100%", maxWidth: "600px"}} />
          {descriptionFeedback && <div className="field-feedback" role="alert">{descriptionFeedback}</div>}
          <input type="submit" value="Create" className="button" style={{width: "90px", marginTop: "5px"}} />
        </form>
      </section>
    </main>
  )
}

export default GameCreatePage;
