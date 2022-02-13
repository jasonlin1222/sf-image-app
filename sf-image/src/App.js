import logo from "./logo.svg";
import "./App.css";
import {
  TextField,
  Typography,
  Container,
  Grid,
  Button,
  ImageList,
  Icon,
  Select,
  MenuItem,
  FormControl,
} from "@mui/material";
import UploadFileIcon from "@mui/icons-material/UploadFile";
import { useState } from "react";
import { grid } from "@mui/system";

function App() {
  const [query, setQuery] = useState("");
  const [file, setFile] = useState(null);
  const [selectModel, setSelectModel] = useState(0);

  const submit = () => {
    fetch(
      "http://localhost:5000/query?query=" + query + "&model=" + selectModel,
      {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      }
    )
      .then((response) => {
        return response.json();
      })
      .then((response) => {
        console.log(response);
      });
  };

  const upload = () => {
    fetch("http://localhost:5000/getfile", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: file,
    })
      .then((response) => {
        return response.json();
      })
      .then((response) => {
        console.log(response);
      });
  };

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
              onChange={(e) => {
                setQuery(e.target.value);
              }}
            />
          </Grid>
          <Grid item container justify="space-between" spacing={3}>
            <Grid item>
              <Button
                data-testid="searchButton"
                variant="contained"
                color="primary"
                onClick={() => {
                  submit();
                }}
              >
                Search
              </Button>
            </Grid>
            <Grid item>
              <FormControl fullWidth>
                <Select
                  label="Select Model Type"
                  required
                  onChange={(e) => {
                    setSelectModel(e.target.value);
                  }}
                >
                  <MenuItem value={1}>OPENAI's CLIP</MenuItem>
                  <MenuItem value={2}>Transformer + ResNet</MenuItem>
                  <MenuItem value={3}>Transformer + ViT</MenuItem>
                  <MenuItem value={4}>LSTM + ResNet</MenuItem>
                  <MenuItem value={5}>LSTM + Vit</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item>
              <Button
                data-testid="uploadButton"
                variant="contained"
                color="primary"
                component="label"
              >
                <UploadFileIcon /> Upload Image
                <input
                  type="file"
                  hidden
                  onChange={(e) => {
                    setFile(e.target.files[0]);
                    upload();
                  }}
                />
              </Button>
            </Grid>
          </Grid>
        </Grid>
        <Grid>
          <ImageList
            sx={{ width: 500, height: 450 }}
            variant="quilted"
            cols={4}
            rowHeight={121}
          ></ImageList>
        </Grid>
      </Grid>
    </Container>
  );
}

export default App;
