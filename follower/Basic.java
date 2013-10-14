public class Basic {
  
  /* I dont know how to commit using the git hub console commands so i just made this as 
   * a text file.
   */
  

	public static int NUM_OF_SENSORS = 3;
	private int[] sensors = new int[NUM_OF_SENSORS];
	boolean[] sensorIO = new boolean[NUM_OF_SENSORS];

	/**
	 * @param args
	 */
	public static void main(String[] args) {
		// TODO Auto-generated method stub

	}

	/**
	 * Converts the numerical value recieved by the sensors and changes it into
	 * a boolean. Done with the purpose of having a way to convert sensor
	 * information to a really simple like a  boolean. 
	 * @param sensorVal
	 *            an array holding numerical sensor values.
	 * @return an array holding the sensor boolean values.
	 */
	public boolean[] sensorValues(int[] sensorVal) {

		for (int i = 0; i < NUM_OF_SENSORS; i++) {
			if (//TODO) {
				sensorIO[i] = false;
			} else {
				sensorIO[i] = true;
			}
		}
		return sensorIO;
	}

	public int move() {
		/*
		 * If the middle sensor shows true for a line below it. TODO add a
		 * method that determines weither most of the right or left side is lit.
		 */
		if (sensorIO[1] && !(sensorIO[0] || sensorIO[2])) {
			System.out.println("Forward");
			
			return 1;
		} else if (sensorIO[2] && !(sensorIO[1] || sensorIO[0])) {
			System.out.println("Right");
			return 2;
		} else if (sensorIO[0] && !(sensorIO[1] || sensorIO[2])) {
			System.out.println("Left");
			return 3;
		} else {
			return -1;
		}
	}
	
	
	public int moveMulit(){
		int halfLength = sensors.length/2;
		int middleSpace = 2;
		
		int left = sum(sensors, 0, halfLength - middleSpace);
		int right = sum(sensors, halfLength + middleSpace, sensors.length);
		int mid = sum(sensors, halfLength - middleSpace / 2, halfLength + middleSpace/2);
		
		if(mid > left || mid > right){
			// go straight
		}
		
		if(left > right) {
			// move to the right
		} else {
			//move to the left
		}
		
		return 0;
	}
	
	/**
	 * sums the values in an array located in a specified range.
	 */
	private int sum(int[] array, int a, int b){
		int sum = 0;
		for(int i = 0; i < b; i++){
			sum += array[i];
		}
		return sum;
	}


	/**
	 * updates the sensor values in whatever way is made to do that
	 * just serves as a fake method to call
	 * @param sensors
	 *            the sensors to set
	 */
	public void setSensors(int[] sensors) {
		this.sensors = sensors;
		sensorValues(sensors);
	}


}
