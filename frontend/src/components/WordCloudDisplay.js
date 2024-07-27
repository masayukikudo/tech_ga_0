import React from 'react';

const WordCloudDisplay = () => {
  const wordCloudUrl = 'http://127.0.0.1:5000/static/images/wordcloud.png';

  return (
    <div>
      {wordCloudUrl ? (
        <img src={wordCloudUrl} alt="Word Cloud" />
      ) : (
        <p>Loading...</p>
      )}
    </div>
  );
};

export default WordCloudDisplay;
