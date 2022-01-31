import logo from './logo.svg';
import './App.css';
import {
  TextField,
  Typography,
  Container,
  Grid,
  Button,
  ImageList,
  Icon
} from "@mui/material";
import UploadFileIcon from '@mui/icons-material/UploadFile';
import { useState } from 'react';

function App() {

  const [query, setQuery] = useState("");

  const submit = () => {
    fetch("http://localhost:5000/query?query=" + query, {
      method:"GET",
      headers: {
        "Content-Type" : "application/json",
      },
    }).then((response) =>{
      return response.json()
    }).then((response) =>{
      console.log(response)
    })
  };

  const upload = () => {

  }

  return (
    <Container maxWidth="md">
    <Grid
      container
      direction="column"
      alignItems="center"
      justify="center"
      style={{ minHeight: "100vh" }}
      spacing={3}
    >
      <Grid item>
        <Typography variant="h2"> Image Search Library </Typography>
      </Grid>
      <Grid item>
        <Typography variant="h5"> seperate keyword by comma (,) </Typography>
      </Grid>
      <Grid item container spacing={3} direction="column">
        <Grid item>
          <TextField
            fullWidth
            id="query"
            label="Query"
            variant="outlined"
            onChange={(e)=>{
              setQuery(e.target.value);
            }}
          />
        </Grid>
        <Grid item container justify="space-between" spacing={70}>
            <Grid item><Button
              data-testid="searchButton"
              variant="contained"
              color="primary"
              onClick={()=>{
                submit();
              }}
            >
              Search
            </Button></Grid>
            <Grid item>
              <Button data-testid="uploadButton" variant="contained" color="primary">
                <UploadFileIcon /> Upload Image
              </Button>
            </Grid>
        </Grid>
      </Grid>
      <Grid>
        <ImageList sx={{ width: 500, height: 450 }} variant="quilted" cols={4} rowHeight={121}>
        </ImageList>
      </Grid>
    </Grid>
  </Container>
  );
}

export default App;
