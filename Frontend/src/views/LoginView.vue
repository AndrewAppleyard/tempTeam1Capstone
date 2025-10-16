<script setup>
import { ref, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import axios from "axios"

const router = useRouter()

const username = ref(null);
const password = ref(null);

async function login() {

  try {

    const response = await axios.post("http://127.0.0.1:5000/Student/login", { // change route

      username: username.value,
      password: password.value,
    })

    alert("Login successful!")
  }
  catch(e) {

    alert("Login failed")
    console.log(e)
  }
}

</script>

<template>
  <v-container fluid class="pa-1" style="background-color: transparent;">
    <h1 style="font-size: 34px;">Welcome to Numa Advising!</h1>

    <v-row justify="center" class="pa-6">
      <v-col cols="12" sm="8" md="6" lg="4">
        <v-card class="pa-5" style="height: 350px; background-color: #BDD5E7; border: 1px solid #002856; border-radius: 12px;">

          <div class="pa-2" style="text-align: left;">
            <label>Username:</label>
            <v-text-field
              v-model="username"
              placeholder="Enter Username"
              hide-details
              dense
              style="background-color: #F5F5F5;"
            ></v-text-field>
          </div>

          <div class="pa-2" style="text-align: left;">
            <label>Password:</label>
            <v-text-field
              v-model="password"
              placeholder="Enter Password"
              type="password"
              hide-details
              dense
              style="background-color: #F5F5F5;"
            ></v-text-field>
          </div>

          <div class="pa-4">
            <v-btn style="align-content: center; background-color: #0032A0; color: #F5F5F5" @click="login">Log in</v-btn>
            <p class="pa-2" style="text-align: center;">Forgot Password</p>
          </div>

        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>