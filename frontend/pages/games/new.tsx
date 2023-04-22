import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import { useAuthContext } from '@/contexts/AuthContext';
import request from "@/functions/request"
import Button from '@/components/Button';
import { GetServerSidePropsContext } from 'next';
import getInitialCookieData from '@/functions/cookies';
import Head from 'next/head';
import { useModalContext } from '@/contexts/ModalContext';

const NewGamePage = () => {
  const router = useRouter();
  const { username, accessToken, refreshToken, setAccessToken, setRefreshToken, setUsername } = useAuthContext();
  const [name, setName] = useState<string>('');
  const [nameFeedback, setNameFeedback] = useState<string>('');
  const [description, setDescription] = useState<string>('');
  const [descriptionFeedback, setDescriptionFeedback] = useState<string>('');
  const { modal, setModal } = useModalContext();
  
  useEffect(() => {
    if (username == '') {
      setModal("sign-in-required");
    }
  }, [username, modal, setModal])

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

    const response = await request('POST', 'games/', accessToken, refreshToken, setAccessToken, setRefreshToken, setUsername, gameData);
    if (response) {
      if (response.status === 201) {
        await router.push('/games');
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
    <>
      <Head>
        <title>Create Game - Republic of Rome Online</title>
      </Head>
      <main id="standard_page" aria-label="Home Page">
        <section className='row'>
          <Button href="..">◀ Back</Button>
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
            <Button formSubmit={true} text="Create" width={80}/>
          </form>
        </section>
      </main>
    </>
  )
}

export default NewGamePage;

export const getServerSideProps = async (context: GetServerSidePropsContext) => {
  const { accessToken, refreshToken, username } = getInitialCookieData(context);
  return {
    props: {
      ssrAccessToken: accessToken,
      ssrRefreshToken: refreshToken,
      ssrUsername: username
    }
  };
};
