import { createClient } from '@supabase/supabase-js'

const supabaseUrl = 'https://swigswqzaqjrjploaixz.supabase.co'
const supabaseAnonKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InN3aWdzd3F6YXFqcmpwbG9haXh6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTEyNjcxOTEsImV4cCI6MjEwNjg0MzE5MX0.7_HM_l1esCsm0q8CZwvov4UJ5Aukh0htpR3uKdOvHpA'

export const supabase = createClient(supabaseUrl, supabaseAnonKey)